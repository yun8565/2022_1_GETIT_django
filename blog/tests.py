from re import S
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.user_lee = User.objects.create_user(username="lee", password="lee123456")
        
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

    def test_category_page(self):
        response = self.client.get(self.category_music.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_music.name, soup.h1.text)
        main_area = soup.find('div', id="main_area")
        self.assertIn(self.category_music.name, main_area.text)
        self.assertIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_001.title, main_area.text)

        