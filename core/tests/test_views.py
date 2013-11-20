from django.test import TestCase


class StackMachineViewsTests(TestCase):

    def test_robots_txt(self):
        response = self.client.get('/robots.txt')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'text/plain')

    def test_blog_feed(self):
        response = self.client.get('/blog/feed.xml')
        self.assertEquals(response.status_code, 200)
