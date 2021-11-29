from django import forms
from django.shortcuts import redirect, render
# Importing libararies for Doc2Vec model and training
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
# before using below line make sure to download stopwords dictionary by using nltk.download("stopwords")
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from .models import Article, User


def index(request):
    is_admin = request.session.get('is_admin')
    arts = Article.objects.values('abstract')
    common_texts_pre = []
    for key, art in enumerate(arts):
        common_texts_pre.append(art['abstract'])

    class ArticleInputForm(forms.Form):
        abstract = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control mb-2'}))

    if request.method == 'POST':
        form = ArticleInputForm(request.POST)
        if form.is_valid():
            new_doc = form.cleaned_data['abstract']

            model = Doc2Vec.load("sars.model")
            # Create new sentence and vectorize it.
            new_sentence = new_doc.split(" ")
            new_sentence_vectorized = model.infer_vector(new_sentence)

            # Calculate cosine similarity.
            similar_sentences = model.docvecs.most_similar(positive=[new_sentence_vectorized])
            output = []
            for i, v in enumerate(similar_sentences):
                ind = v[0]
                output.append(common_texts_pre[ind])

            context = {
                'arts': output,
                'is_admin': is_admin,
            }
            return render(request, 'articles/articles_rec.html', context)

    else:
        form = ArticleInputForm()

    context = {
        'is_admin': is_admin,
        'form': form
    }
    return render(request, 'articles/index.html', context)


def login(request):
    class UserLoginForm(forms.ModelForm):
        class Meta:
            model = User
            fields = ['username', 'pswd']
            widgets = {
                'username': forms.TextInput(attrs={'class': 'form-control mb-2'}),
                'pswd': forms.PasswordInput(attrs={'class': 'form-control mb-2'})
            }

    form = UserLoginForm()
    error_msg = None

    if request.method == "POST":
        f_username = request.POST.get('username')
        f_pswd = request.POST.get('pswd')

        user = User.get_user_by_username(f_username)

        if user:
            if f_pswd == user.pswd:
                if user.status:
                    request.session['user'] = user.id
                    request.session['is_admin'] = user.is_admin
                    return redirect("index")
                else:
                    error_msg = "Your account is not approved!"
            else:
                error_msg = "Incorrect Password"

        else:
            error_msg = "User Doesn't Exist"

    context = {
        'form': form,
        'error_msg': error_msg,
    }

    return render(request, 'articles/login.html', context)


def logout(request):
    request.session['user'] = None

    return redirect('login')


def register(request):
    class AddUserForm(forms.ModelForm):
        class Meta:
            model = User
            fields = ['name', 'username', 'pswd']

            widgets = {
                'name': forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'John Doe'}),
                'username': forms.TextInput(attrs={'class': 'form-control mb-2'}),
                'pswd': forms.PasswordInput(attrs={'class': 'form-control mb-2'}),
            }

    form = AddUserForm()

    if request.method == "POST":
        form = AddUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")

    context = {
        'form': form,
    }

    return render(request, 'articles/register.html', context)


def manage_users(request):
    current_user = request.session['user']
    is_admin = request.session.get('is_admin')
    users = User.objects.all()

    if request.method == "POST":
        if request.POST.get("approve"):
            user_id = request.POST.get("approve")
            user = User.objects.get(id=user_id)
            user.status = True
            user.save()
        if request.POST.get("unapprove"):
            user_id = request.POST.get("unapprove")
            user = User.objects.get(id=user_id)
            user.status = False
            user.save()
        if request.POST.get("remove"):
            user_id = request.POST.get("remove")
            user = User.objects.get(id=user_id).delete()
            # user.status = False
        return redirect("manage_users")

    context = {
        'users': users,
        'current_user': current_user,
        'is_admin': is_admin,
    }
    return render(request, 'articles/manage_users.html', context)


def articles(request):
    is_admin = request.session.get('is_admin')
    arts = Article.objects.all().order_by("-id")

    context = {
        'arts': arts,
        'is_admin': is_admin
    }
    return render(request, 'articles/articles.html', context)


def article(request, pk):
    is_admin = request.session.get('is_admin')
    art = Article.get_article_by_pk(pk)

    context = {
        'art': art,
        'is_admin': is_admin
    }

    return render(request, 'articles/article.html', context)


def add_article(request):
    is_admin = request.session.get('is_admin')

    class ArticleForm(forms.ModelForm):
        class Meta:
            model = Article
            fields = ['title', 'author', 'area', 'abstract']

            widgets = {
                'title': forms.TextInput(attrs={'class': 'form-control mb-2'}),
                'author': forms.TextInput(attrs={'class': 'form-control mb-2'}),
                'abstract': forms.Textarea(attrs={'class': 'form-control mb-2'}),
                'area': forms.TextInput(attrs={'class': 'form-control mb-2'}),
            }

    form = ArticleForm()

    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            form.save()
            # Training the model
            arts = Article.objects.values('abstract')
            common_texts_pre = []
            for key, art in enumerate(arts):
                common_texts_pre.append(art['abstract'])

            common_texts = common_texts_pre
            common_texts = [word_tokenize(sw_removed.lower()) for sw_removed in common_texts if
                            not sw_removed in stopwords.words()]

            # Tagging documents. Each sentences(set of words) are mapped unique index.
            # Tagged documents are input for doc2vec model.
            tagged_data = []
            for i, doc in enumerate(common_texts):
                tagged = TaggedDocument(doc, [i])
                tagged_data.append(tagged)

            max_epochs = 100
            vec_size = 20
            alpha = 0.025

            model = Doc2Vec(vector_size=vec_size,
                            alpha=alpha,
                            min_alpha=0.00025,
                            min_count=1,
                            dm=1)

            model.build_vocab(tagged_data)

            for epoch in range(max_epochs):
                print('iteration{0}'.format(epoch))
                model.train(tagged_data,
                            total_examples=model.corpus_count,
                            epochs=model.epochs)

                # Decrease the learning rate
                model.alpha -= 0.0002

                # fix the learning rate, no decay
                model.min_alpha = model.alpha

            model.save("sars.model")
            print("Model Saved")
            return redirect("add_article")

    context = {
        'form': form,
        'is_admin': is_admin
    }
    return render(request, 'articles/add_article.html', context)
