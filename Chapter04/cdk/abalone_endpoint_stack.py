import os
import aws_cdk as cdk
import aws_cdk.aws_sagemaker as sagemaker

class EndpointStack(cdk.Stack):
    def __init__(self, app: cdk.App, id: str, *, model_name: str=None, **kwargs) -> None:
        super().__init__(app, id, **kwargs)
        
        bucket_name = cdk.CfnParameter(
            self,
            "BucketName",
            type="String"
        )
        
        execution_id = cdk.CfnParameter(
            self,
            "ExecutionId",
            type="String"
        )
        
        model_uri = cdk.CfnParameter(
            self,
            "ModelUri",
            type="String"
        )
        
        execution_role = cdk.CfnParameter(
            self,
            "ExecutionRole",
            type="String"
        )
        
        model_image = cdk.CfnParameter(
            self,
            "ImageUri",
            type="String"
        )
        
        model = sagemaker.CfnModel(
            self,
            "Model",
            model_name="{}-model-{}".format(model_name.capitalize(), execution_id.value_as_string),
            execution_role_arn=execution_role.value_as_string,
            primary_container=sagemaker.CfnModel.ContainerDefinitionProperty(
                image=model_image.value_as_string,
                model_data_url=model_uri.value_as_string,
                image_config=sagemaker.CfnModel.ImageConfigProperty(
                    repository_access_mode="Platform"
                )
            )
        )
        
        endpoint_config = sagemaker.CfnEndpointConfig(
            self,
            "EndpointConfig",
            endpoint_config_name="{}-config-{}".format(model_name.capitalize(), execution_id.value_as_string),
            production_variants=[
                sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                    initial_instance_count=2,
                    initial_variant_weight=1.0,
                    instance_type="ml.t3.medium",
                    model_name=model.attr_model_name,
                    variant_name="AllTraffic"
                )
            ],
            data_capture_config=sagemaker.CfnEndpointConfig.DataCaptureConfigProperty(
                capture_content_type_header=sagemaker.CfnEndpointConfig.CaptureContentTypeHeaderProperty(
                    csv_content_types=[
                        "text/csv"
                    ]
                ),
                capture_options=[
                    sagemaker.CfnEndpointConfig.CaptureOptionProperty(capture_mode="Input"),
                    sagemaker.CfnEndpointConfig.CaptureOptionProperty(capture_mode="Output")
                ],
                destination_s3_uri="s3://{}/endpoint-data-capture".format(bucket_name.value_as_string),
                enable_capture=True,
                initial_sampling_percentage=100.0
            )
        )
        endpoint_config.add_depends_on(model)
        
        endpoint = sagemaker.CfnEndpoint(
            self,
            "AbaloneEndpoint",
            endpoint_config_name=endpoint_config.attr_endpoint_config_name,
            endpoint_name="{}-Endpoint".format(model_name.capitalize())
        )
        endpoint.add_depends_on(endpoint_config)
