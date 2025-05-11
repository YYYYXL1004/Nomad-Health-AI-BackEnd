# 医疗问答 API 文档

**服务描述**: 本API基于Qwen-7B微调模型（`qwen7b_lora_yiliao.gguf`），提供中文和蒙文的医疗问答服务。

**基础URL**: `http://<服务器IP或域名>:8000`

在校园网环境下，'http://183.175.12.124:8000'

(请将 `<服务器IP或域名>` 替换为API服务实际部署的地址。如果通过ngrok等隧道服务暴露，请使用ngrok提供的URL。)

## 1. 医疗问答接口

这是核心的问答功能接口。

* **端点 (Endpoint)**: `/api/medical_qa`
* **方法 (Method)**: `POST`
* **请求格式 (Request Format)**: JSON
* **请求头 (Request Headers)**:
    * `Content-Type: application/json`

* **请求体参数 (Request Body Parameters)**:

    | 参数名        | 类型    | 是否必需 | 默认值   | 描述                                                                 |
    | ------------- | ------- | -------- | -------- | -------------------------------------------------------------------- |
    | `query`       | string  | 是       | N/A      | 用户提出的医疗问题文本。                                                 |
    | `max_tokens`  | integer | 否       | `2048`   | 模型生成的最大token数量（回答长度的上限）。                                |
    | `temperature` | float   | 否       | `0.7`    | 控制生成文本的随机性。较低的值使输出更确定和保守，较高的值使输出更多样和有创意。 |
    | `top_p`       | float   | 否       | `0.95`   | 控制核心采样的概率阈值。模型会从累积概率大于`top_p`的token中进行采样。          |
    | `language`    | string  | 否       | `chinese`| 指定问题的语言和期望回答的语言。支持的值为: `"chinese"` 或 `"mongolian"`。 |

* **请求示例 (Request Example)**:
    ```json
    {
      "query": "高血压患者日常应该注意什么？",
      "max_tokens": 512,
      "temperature": 0.6,
      "language": "chinese"
    }
    ```
    蒙文请求示例:
    ```json
    {
      "query": "Цусны даралт өндөр өвчтөн өдөр тутамд юу анхаарах вэ?",
      "max_tokens": 512,
      "language": "mongolian"
    }
    ```

* **响应格式 (Response Format)**: JSON

* **成功响应 (Success Response)**:
    * **状态码 (Status Code)**: `200 OK`
    * **响应体 (Response Body)**:
        | 参数名       | 类型   | 描述                       |
        | ------------ | ------ | -------------------------- |
        | `response`   | string | 模型生成的回答文本。         |
        | `time_taken` | float  | 处理该请求所花费的时间（秒）。 |

    * **成功响应示例 (Success Response Example)**:
        ```json
        {
          "response": "高血压患者日常应注意低盐饮食，规律作息，监测血压，遵医嘱服药，并进行适当的体育锻炼。",
          "time_taken": 5.32
        }
        ```

* **错误响应 (Error Responses)**:
    * **状态码 (Status Code)**: `400 Bad Request`
        * **原因**: 请求参数无效（例如，`language` 参数不是 "chinese" 或 "mongolian"）。
        * **响应体示例**:
            ```json
            {
              "detail": "语言参数无效，支持'chinese'或'mongolian'"
            }
            ```
    * **状态码 (Status Code)**: `422 Unprocessable Entity`
        * **原因**: 请求体JSON格式不正确或缺少必需字段 (例如缺少 `query`)。FastAPI会自动处理。
        * **响应体示例**:
            ```json
            {
              "detail": [
                {
                  "loc": [
                    "body",
                    "query"
                  ],
                  "msg": "field required",
                  "type": "value_error.missing"
                }
              ]
            }
            ```
    * **状态码 (Status Code)**: `500 Internal Server Error`
        * **原因**: 模型推理过程中发生内部错误。
        * **响应体示例**:
            ```json
            {
              "detail": "模型推理错误: <具体错误信息>"
            }
            ```
    * **状态码 (Status Code)**: `503 Service Unavailable`
        * **原因**: 模型尚未加载或加载失败。
        * **响应体示例**:
            ```json
            {
              "detail": "模型尚未加载或加载失败，请稍后再试或检查服务器日志。"
            }
            ```

## 2. 健康检查接口

用于检查API服务和模型是否正常运行。

* **端点 (Endpoint)**: `/health`
* **方法 (Method)**: `GET`
* **请求参数 (Request Parameters)**: 无

* **成功响应 (Success Response)**:
    * **状态码 (Status Code)**: `200 OK`
    * **响应体 (Response Body)**:
        | 参数名                      | 类型   | 描述                                                             |
        | --------------------------- | ------ | ---------------------------------------------------------------- |
        | `status`                    | string | 服务状态，通常为 `"healthy"`。                                     |
        | `model_path`                | string | 当前加载的模型文件路径。                                               |
        | `n_gpu_layers_configured`   | string/integer | 配置的GPU层数（可能是数字或"N/A"）。                                |
        | `target_main_gpu_configured`| integer|  代码中 `Llama()` 初始化时配置的 `main_gpu` 参数值（或硬编码的显示值）。 |
    * **成功响应示例 (Success Response Example)**:
        ```json
        {
          "status": "healthy",
          "model_path": "/sda/data/yaoxianglin/Qwen_YIliao/models/qwen7b_lora_yiliao.gguf",
          "n_gpu_layers_configured": 29, 
          "target_main_gpu_configured": 0 
        }
        ```
        *(注意: `target_main_gpu_configured` 在您的 `main.py` 中当前硬编码为4，但如果配合`CUDA_VISIBLE_DEVICES`使用，实际程序内部使用的`main_gpu`参数应为0。健康检查接口的此字段可能需要调整以准确反映实际配置。)*

* **模型未加载时的响应 (Model Not Loaded Response)**:
    * **状态码 (Status Code)**: `200 OK` (虽然是200，但内容表明不健康)
    * **响应体示例**:
        ```json
        {
          "status": "unhealthy",
          "reason": "Model not loaded",
          "model_path": "/sda/data/yaoxianglin/Qwen_YIliao/models/qwen7b_lora_yiliao.gguf"
        }
        ```

## 3. 交互式API文档 (Swagger UI)

服务启动后，可以通过浏览器访问 `http://<服务器IP或域名>:8000/docs` 来查看和使用交互式的API文档界面（由Swagger UI提供）。在这里可以直接测试各个端点。

---

**使用说明和注意事项:**

* **模型加载时间**: 服务启动时会加载模型，这可能需要一些时间。在模型完全加载之前，`/api/medical_qa` 接口可能返回503错误。可以通过 `/health` 接口检查模型加载状态。
* **性能**: API的响应时间取决于服务器硬件配置（特别是GPU）、模型的卸载层数 (`n_gpu_layers`)、请求的 `max_tokens` 以及当前服务器的负载。
* **错误处理**: 调用方APP应妥善处理可能出现的HTTP错误状态码和响应体中的错误信息。
* **并发处理**: FastAPI基于ASGI，能够处理并发请求。但实际并发性能受限于底层模型推理的并发能力和硬件资源。
