from flask import Blueprint
from flask_restx import Api

from image_segmentation.object_classification.classifier import ObjectClassifier
from image_segmentation.object_classification.feature_extraction import FeatureSimilarity, ColorSimilarity
from image_segmentation.object_detection.object_segmentation import ObjectSegmentation
from objects_counter.consts import SAM_CHECKPOINT, SAM_MODEL_TYPE


class FixedApi(Api):
    def ns_urls(self, ns, urls):
        def fix(url):
            return url[1:] if url.startswith('//') else url

        return [fix(url) for url in super().ns_urls(ns, urls)]


blueprint = Blueprint('api', __name__, url_prefix='/api')
api = FixedApi(blueprint)
sam = ObjectSegmentation(SAM_CHECKPOINT, model_type=SAM_MODEL_TYPE)
feature_similarity_model = FeatureSimilarity()
color_similarity_model = ColorSimilarity()
object_grouper = ObjectClassifier(sam, feature_similarity_model, color_similarity_model)
