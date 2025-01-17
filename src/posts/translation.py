from modeltranslation.translator import TranslationOptions, translator

from src.posts.models.categ_model import Category
from src.posts.models.post_model import Post


class PostTranslationOptions(TranslationOptions):
    fields = ("title", "content")


class CategoryTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(Post, PostTranslationOptions)
translator.register(Category, CategoryTranslationOptions)
