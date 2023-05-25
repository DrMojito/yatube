from django.urls import reverse_lazy
from django.views.generic import TemplateView


class AboutAuthorView(TemplateView):
    success_url = reverse_lazy('posts:index')
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    success_url = reverse_lazy('posts:index')
    template_name = 'about/tech.html'
