
#include <iostream>
#include <vector>
#include <algorithm>
#include <cstring>
#include <cmath>

#include "nvdsinfer_custom_impl.h"

extern "C" bool NvDsInferParseCustomYoloE(
    std::vector<NvDsInferLayerInfo> const& outputLayersInfo,
    NvDsInferNetworkInfo const& networkInfo,
    NvDsInferParseDetectionParams const& detectionParams,
    std::vector<NvDsInferParseObjectInfo>& objectList)
{
    const int NUM_CLASSES = 80;
    const int NUM_ANCHORS = 8400;

    const char* OUTPUT_NAME = "output0";

    // Find the YOLOv11 output tensor
    const NvDsInferLayerInfo* outputLayer = nullptr;

    for (const auto& layer : outputLayersInfo) {
        if (layer.layerName &&
            std::strcmp(layer.layerName, OUTPUT_NAME) == 0) {
            outputLayer = &layer;
            break;
        }
    }

    if (outputLayer == nullptr || outputLayer->buffer == nullptr) {
        std::cerr << "YOLOv11 output tensor not found!" << std::endl;
        return false;
    }

    // Expected output: [84, 8400]
    if (outputLayer->inferDims.numDims != 2 ||
        outputLayer->inferDims.d[0] != 84 ||
        outputLayer->inferDims.d[1] != NUM_ANCHORS) {
        std::cerr << "Unexpected YOLOv11 output dimensions!"
                  << std::endl;
        return false;
    }

    const float* data =
        static_cast<const float*>(outputLayer->buffer);

    const float netW = static_cast<float>(networkInfo.width);
    const float netH = static_cast<float>(networkInfo.height);

    // Decode each prediction
    for (int i = 0; i < NUM_ANCHORS; i++) {

        float cx = data[0 * NUM_ANCHORS + i];
        float cy = data[1 * NUM_ANCHORS + i];
        float bw = data[2 * NUM_ANCHORS + i];
        float bh = data[3 * NUM_ANCHORS + i];

        float maxScore = 0.0f;
        int maxClass = 0;

        // Find the highest scoring class
        for (int c = 0; c < NUM_CLASSES; c++) {

            float score =
                data[(4 + c) * NUM_ANCHORS + i];

            if (score > maxScore) {
                maxScore = score;
                maxClass = c;
            }
        }

        // Apply confidence threshold
        float threshold =
            detectionParams.perClassPreclusterThreshold[maxClass];

        if (maxScore < threshold) {
            continue;
        }

        // Convert center coordinates to bounding box
        float left = cx - (bw / 2.0f);
        float top = cy - (bh / 2.0f);

        float right = cx + (bw / 2.0f);
        float bottom = cy + (bh / 2.0f);

        // Clip bounding box to network dimensions
        left = std::max(0.0f, left);
        top = std::max(0.0f, top);

        right = std::min(netW, right);
        bottom = std::min(netH, bottom);

        if (right <= left || bottom <= top) {
            continue;
        }

        NvDsInferParseObjectInfo object;

        object.left = left;
        object.top = top;
        object.width = right - left;
        object.height = bottom - top;

        object.detectionConfidence = maxScore;
        object.classId = static_cast<unsigned int>(maxClass);

        objectList.push_back(object);
    }

    return true;
}

// Verify parser function signature
CHECK_CUSTOM_PARSE_FUNC_PROTOTYPE(NvDsInferParseCustomYoloE);
