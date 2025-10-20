from django import forms
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.core.files.base import ContentFile
from django.db.models import Q
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
    CreateView,
    DeleteView,
    UpdateView,
    View,
)
from .models import Score, ScoreFile
from .consts import ITEM_PER_PAGE
from .utils import detect_and_split_pages  # ← トリミング関数
import os
from cloudinary.uploader import upload
from io import BytesIO


class ListScoreView(ListView):
    template_name = 'score/score_list.html'
    model = Score
    paginate_by = ITEM_PER_PAGE

    def get_queryset(self):
        score_list = Score.objects.all()
        query = self.request.GET.get('query')
        query_title = self.request.GET.get('title')
        query_comp = self.request.GET.get('comp')
        query_arr = self.request.GET.get('arr')
        query_category = self.request.GET.get('category')
        sort = self.request.GET.get('sort', 'title')#表示順　デフォルトは曲名 

        #検索機能
        if query:#キーワード検索
            score_list = score_list.filter(
                Q(title__icontains=query) | Q(comp__icontains=query) | Q(arr__icontains=query) | Q(category__icontains=query)
            )
        else:#詳細検索
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
    model = Score
    fields = ['title', 'comp', 'arr', 'category']
    template_name = 'score/score_create.html'
    success_url = reverse_lazy('list-score')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        files = request.FILES.getlist('files')

        if form.is_valid():
            score = form.save()

            for uploaded_file in files:
                ext = os.path.splitext(uploaded_file.name)[1].lower()

                # PDF → そのまま保存
                if ext == '.pdf':
                    ScoreFile.objects.create(score=score, file=uploaded_file)

                # 画像 → PDF化してCloudinaryに直接アップロード
                elif ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                    tmp_path = os.path.join('/tmp', uploaded_file.name)
                    with open(tmp_path, 'wb+') as tmp:
                        for chunk in uploaded_file.chunks():
                            tmp.write(chunk)

                    pdf_bytes = detect_and_split_pages(tmp_path)
                    if pdf_bytes:
                        # Cloudinary に直接アップロード
                        pdf_content = pdf_bytes.read()
                        upload_result = upload(
                            pdf_content,
                            folder="scores/files",
                            resource_type="auto",
                            public_id=os.path.splitext(uploaded_file.name)[0] + "_converted",
                            format="pdf"
                        )
                        ScoreFile.objects.create(
                            score=score,
                            file=upload_result["public_id"]
                        )
                    else:
                        # PDF変換失敗時は元画像をアップロード
                        ScoreFile.objects.create(score=score, file=uploaded_file)

            return redirect(self.success_url)

        return self.form_invalid(form)


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


#def index_view(request):
#    object_list = Score.objects.order_by()
#
#    paginator = Paginator(object_list, ITEM_PER_PAGE)
#    page_number = request.GET.get('page',1)
#    page_obj = paginator.page(page_number)
#    
#
#
#    return render(request, 'score/index.html', {'object_list': object_list, 'page_obj':page_obj },)

class ScorePdfView(DetailView):
    template_name = "score/score_pdf.html"
    model = Score

class SearchScoreView(View):
    template_name = "score/score_search.html"

    def get(self, request, *args, **kwargs):
        query_params = request.GET.urlencode()
        if query_params:
            url = reverse('list-score') + f'?{query_params}'
            return redirect(url)
        # パラメータがないときはテンプレートを表示
        from django.shortcuts import render
        return render(request, self.template_name)