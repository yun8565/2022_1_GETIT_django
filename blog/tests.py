from re import S
import re
from turtle import up, update
from urllib import response
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Comment

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.user_lee = User.objects.create_user(username="lee", password="lee123456")
        self.user_chang = User.objects.create_user(username="chang", password="lee123456")

        self.user_chang.is_staff = True
        self.user_chang.save()

        self.category_music = Category.objects.create(name="음악", slug="음악")
        
        self.tag_python = Tag.objects.create(name="파이썬", slug="파이썬")
        self.tag_java = Tag.objects.create(name="자바", slug="자바")
        self.tag_js = Tag.objects.create(name="자바스크립트", slug="자바스크립트")

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content = '카테고리가 없어요.. 미분류입니다',
            author=self.user_lee,
        )
        self.post_001.tags.add(self.tag_python)

        self.post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content = '카테고리가 있어요',
            author=self.user_lee,
            category=self.category_music,
        )

        self.post_003 = Post.objects.create(
            title='세 번째 포스트입니다.',
            content = '태그가 많아요',
            author=self.user_lee,
            category=self.category_music
        )
        self.post_003.tags.add(self.tag_java)
        self.post_003.tags.add(self.tag_js)

        self.comment_001 = Comment.objects.create(
            post=self.post_001,
            author=self.user_lee,
            content="첫 번째 댓글입니다."
        )


    def category_card_test(self,soup):
        categories_card = soup.find('div', id='categories_card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(
            f'{self.category_music.name} ({self.category_music.post_set.count()})',
            categories_card.text
        )
        self.assertIn(f'미분류 (1)', categories_card.text)

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)
        
        logo_btn = navbar.find('a', text='Do It Django')
        self.assertEqual(logo_btn.attrs['href'], "/")
        
        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], "/")
        
        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], "/blog/")
        
        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], "/about_me/")
    
    def test_post_list(self):
        self.assertEqual(Post.objects.count(),3)
    
        response = self.client.get('/blog/')
    
        self.assertEqual(response.status_code, 200)
    
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')
    
        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main_area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)
        
        post_001_card = main_area.find('div', id='post-1')
        self.assertIn('미분류', post_001_card.text)
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.user_lee.username.upper(), post_001_card.text)
        self.assertIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_java.name, post_001_card.text)
        self.assertNotIn(self.tag_js.name, post_001_card.text)

        post_002_card=main_area.find('div', id="post-2")
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertIn(self.user_lee.username.upper(), post_002_card.text)
        self.assertNotIn(self.tag_java.name, post_002_card.text)
        self.assertNotIn(self.tag_js.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)


        post_003_card=main_area.find('div', id="post-3")
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.post_003.category.name, post_003_card.text)
        self.assertIn(self.user_lee.username.upper(), post_003_card.text)
        self.assertIn(self.tag_java.name, post_003_card.text)
        self.assertIn(self.tag_js.name, post_003_card.text)
        self.assertNotIn(self.tag_python.name, post_003_card.text)

        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(),0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main_area')
        #self.assertNotIn('아직 게시물이 없습니다', main_area.text)
        
    def test_post_detail(self):
        self.assertEqual(self.post_003.get_absolute_url(), '/blog/3/')
        
        response= self.client.get(self.post_003.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.navbar_test(soup)
        self.category_card_test(soup)
    
        self.assertIn(self.post_003.title, soup.title.text)
        
        main_area = soup.find('div', id='main_area')
        post_area = main_area.find('div', id='post_area')
        self.assertIn(self.post_003.title, post_area.text)
        self.assertIn(self.category_music.name, post_area.text)
        
        self.assertIn(self.user_lee.username.upper(),post_area.text)
        self.assertIn(self.post_003.content, post_area.text)

        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertIn(self.tag_java.name, post_area.text)
        self.assertIn(self.tag_js.name, post_area.text)

        comments_area = soup.find('div', id='comment_area')
        comment_001_area = comments_area.find('div', id='comment-1')
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)

    def test_category_page(self):
        response = self.client.get(self.category_music.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_music.name, soup.h1.text)
        main_area = soup.find('div', id="main_area")
        self.assertIn(self.category_music.name, main_area.text)

        self.assertNotIn(self.post_001.title, main_area.text)
        self.assertIn(self.post_002.title, main_area.text)
        self.assertIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_java.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_java.name, soup.h1.text)
        
        main_area = soup.find('div', id="main_area")
        self.assertIn(self.tag_java.name, main_area.text)
        self.assertNotIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertIn(self.post_003.title, main_area.text)
        
    def test_create_post(self):
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code,200)

        #lee는 권한없음
        self.client.login(username='lee', password='lee123456')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code,200)

        self.client.login(username='chang', password='lee123456')

        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code,200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main_area')
        self.assertIn('Create New Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            '/blog/create_post/',
            {
                'title' : 'Post Form 만들기',
                'content' : 'Post Form 페이지를 만듭시다.',
                'tags_str' : 'new tag; 한글 태그, 파이썬'
            }
        )
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.author.username, "chang")

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name= '한글 태그'))
        self.assertEqual(Tag.objects.count(), 5)

    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code,200)

        self.assertNotEqual(self.post_003.author, self.user_chang)
        self.client.login(username=self.user_chang.username,password="lee123456")
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code,403)

        self.client.login(username=self.post_003.author.username,password="lee123456")
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code,200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main_area')
        self.assertIn('Edit Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('자바;자바스크립트', tag_str_input.attrs['value'])

        response = self.client.post(
            update_post_url,
            {
                'title':'세 번째 포스트를 수정함',
                'content': '하이',
                'category': self.category_music.pk,
                'tags_str' : '파이썬 공부; 한글 태그, some tag'
            },
            follow=True
        )

        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main_area')
        self.assertIn('세 번째 포스트를 수정함', main_area.text)
        self.assertIn('하이', main_area.text)
        self.assertIn(self.category_music.name, main_area.text)

        self.assertIn('파이썬 공부', main_area.text)
        self.assertIn('한글 태그', main_area.text)
        self.assertIn('some tag', main_area.text)
        self.assertNotIn('자바', main_area.text)