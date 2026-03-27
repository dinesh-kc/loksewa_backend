from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['home', 'about', 'contact', 'privacy_policy', 'terms_of_service', 'bookmark_list', 'daily_revision','loksewa_preparation', 'online_loksewa_class', 'online_loksewa_mcq']
    
    def location(self, item):
        return reverse(item)

# If you have blog posts or articles, add this too
# class ArticleSitemap(Sitemap):
#     priority = 0.9
#     changefreq = 'daily'

#     def items(self):
#         # Replace with your actual Article model
#         from your_app.models import Article
#         return Article.objects.all()
    
#     def lastmod(self, obj):
#         return obj.updated_at  # or created_at