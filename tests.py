import unittest
from parsing.parsing import Parser


class TestParser(unittest.TestCase):

    def test_keywords(self):
        parser = Parser()

        with open('templates/1.html') as file:
            tree = parser.get_tree(file.read())
            keywords = parser.get_keywords(tree)
            self.assertEqual(keywords, ['test', '1', 'parser'])

        with open('templates/2.html') as file:
            tree = parser.get_tree(file.read())
            keywords = parser.get_keywords(tree)
            self.assertEqual(keywords, ['test', '2', 'parser'])

        with open('templates/3.html') as file:
            tree = parser.get_tree(file.read())
            keywords = parser.get_keywords(tree)
            self.assertEqual(keywords, [])

        with open('templates/4.html') as file:
            tree = parser.get_tree(file.read())
            keywords = parser.get_keywords(tree)
            self.assertEqual(keywords, ['test', 'spaces', 'parser'])

    def test_headers(self):
        parser = Parser()

        with open('templates/1.html') as file:
            tree = parser.get_tree(file.read())
            headers = parser.get_headers(tree)
            self.assertEqual(headers, {
                'h1': ['Header 1'],
                'h2': ['Header 2', 'Header 2'],
            })

        with open('templates/2.html') as file:
            tree = parser.get_tree(file.read())
            headers = parser.get_headers(tree)
            self.assertEqual(headers, {
                'h1': ['Header 1'],
                'h2': ['Header 2'],
                'h3': ['Header 3'],
                'h4': ['Header 4'],
                'h5': ['Header 5'],
                'h6': ['Header 6']
            })

        with open('templates/3.html') as file:
            tree = parser.get_tree(file.read())
            headers = parser.get_headers(tree)
            self.assertEqual(headers, {})

        with open('templates/4.html') as file:
            tree = parser.get_tree(file.read())
            headers = parser.get_headers(tree)
            self.assertEqual(headers, {
                'h1': [
                    'Header 1', 'Header 1', 'Header 1',
                    'Header 1', 'Header 1', 'Header 1'
                ]
            })
            self.assertEqual(len(headers.get('h1')), 6)

    def test_title(self):
        parser = Parser()

        with open('templates/1.html') as file:
            tree = parser.get_tree(file.read())
            title = parser.get_title(tree)
            self.assertEqual(title, 'Test 1')

        with open('templates/2.html') as file:
            tree = parser.get_tree(file.read())
            title = parser.get_title(tree)
            self.assertEqual(title, '')

        with open('templates/3.html') as file:
            tree = parser.get_tree(file.read())
            title = parser.get_title(tree)
            self.assertEqual(title, None)

        with open('templates/4.html') as file:
            tree = parser.get_tree(file.read())
            title = parser.get_title(tree)
            self.assertEqual(title, 'Test 4')

    def test_images(self):
        parser = Parser()

        with open('templates/1.html') as file:
            tree = parser.get_tree(file.read())
            images = parser.get_images(tree)
            self.assertEqual(images, ['1.jpg', '2.png', '3.svg'])

        with open('templates/2.html') as file:
            tree = parser.get_tree(file.read())
            images = parser.get_images(tree)
            self.assertEqual(images, ['/static/images/logo.jpg'])

        with open('templates/3.html') as file:
            tree = parser.get_tree(file.read())
            images = parser.get_images(tree)
            self.assertEqual(images, [])

        with open('templates/4.html') as file:
            tree = parser.get_tree(file.read())
            images = parser.get_images(tree)
            self.assertEqual(images, [''])

    def test_links(self):
        parser = Parser()

        with open('templates/1.html') as file:
            tree = parser.get_tree(file.read())
            links = parser.get_links(tree)
            self.assertEqual(links, ['http://google.com', 'http://fb.com'])

        with open('templates/2.html') as file:
            tree = parser.get_tree(file.read())
            links = parser.get_links(tree)
            self.assertEqual(
                links, ['http://google.com', 'https://google.com'])

        with open('templates/3.html') as file:
            tree = parser.get_tree(file.read())
            links = parser.get_links(tree)
            self.assertEqual(links, [])

        with open('templates/4.html') as file:
            tree = parser.get_tree(file.read())
            links = parser.get_links(tree)
            self.assertEqual(links, ['https://instagram.com'])


if __name__ == '__main__':
    unittest.main()
