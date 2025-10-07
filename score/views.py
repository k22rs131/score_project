from django import forms
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.core.files.base import ContentFile
from django.db.models import Q
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
    CreateView,
    DeleteView,
    UpdateView
)
from .models import Score, Post
from .consts import ITEM_PER_PAGE
from .utils import detect_and_split_pages


class ListScoreView(ListView):
    template_name = 'score/score_list.html'
    model = Score
    paginate_by = ITEM_PER_PAGE

    def get_queryset(self):
        score_list = Score.objects.all()
        query_title = self.request.GET.get('title')
        query_comp = self.request.GET.get('comp')
        query_arr = self.request.GET.get('arr')
        query_category = self.request.GET.get('category')
        sort = self.request.GET.get('sort', 'title')#表示順　デフォルトは曲名 

        #検索機能
        if query_title:
            score_list = score_list.filter(title__icontains=query_title)
        
        if query_comp:
            score_list = score_list.filter(comp__icontains=query_comp)
        
        if query_arr:
            score_list = score_list.filter(arr__icontains=query_arr)
        
        if query_category:
            score_list = score_list.filter(category__icontains=query_category)
        
        
        allowed_sorts = ['title', '-title', 'comp', '-comp', 'arr', '-arr' ]
        if sort in allowed_sorts:
            score_list = score_list.order_by(sort)

        return score_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.request.GET.get('title', '')
        context['comp'] = self.request.GET.get('comp', '')
        context['arr'] = self.request.GET.get('arr', '')
        context['category'] = self.request.GET.get('category', '')
        context['sort'] = self.request.GET.get('sort','title')
        return context



def post_list(request):
    posts = Post.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts})


class DetailScoreView(DetailView):
    template_name = 'score/score_detail.html'
    model = Score
    success_url = reverse_lazy('list-score')

class CreateScoreView(CreateView):
    template_name = 'score/score_create.html'
    model = Score
    fields = ('title','comp','arr','category')#,'image_file')

    #def form_valid(self, form):
    #    self.object = form.save(commit=False)
    #    self.object.save()  # image_file を一旦保存

        #if self.object.image_file:
        #    img_path = self.object.image_file.path
        #    print("DEBUG: img_path =", img_path)

            # OpenCVで処理してPDF生成
        #    pdf_bytes = detect_and_split_pages(img_path)

        #    if pdf_bytes:
        #        self.object.pdf_file.save(
        #            f"{self.object.title}.pdf",
        #            ContentFile(pdf_bytes.read()),  # BytesIO から読み出し
        #            save=False
        #        )
        #        self.object.save()
        #    else:
        #        print("DEBUG: PDF が生成されませんでした")

        #return super().form_valid(form)

    success_url = reverse_lazy('list-score')

class DeleteScoreView(DeleteView):
    template_name = 'score/score_delete.html'
    model = Score
    success_url = reverse_lazy('list-score')

class UpdateScoreView(UpdateView):
    template_name = 'score/score_update.html'
    model = Score
    fields = ('title','comp','arr','category')
    success_url = reverse_lazy('list-score')

class IndexScoreView(TemplateView):
    template_name = 'score/score_index.html'
    model = Score
    success_url = reverse_lazy('detail-score')


def index_view(request):
    object_list = Score.objects.order_by()

    paginator = Paginator(object_list, ITEM_PER_PAGE)
    page_number = request.GET.get('page',1)
    page_obj = paginator.page(page_number)
    


    return render(request, 'score/index.html', {'object_list': object_list, 'page_obj':page_obj },)

class ScorePdfView(DetailView):
    template_name = "score/score_pdf.html"
    model = Score
