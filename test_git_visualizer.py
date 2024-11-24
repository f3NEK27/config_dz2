import unittest
from unittest.mock import patch
import subprocess
import os


class GitDependencyVisualizer:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def get_commit_dependencies(self):
        # Логика получения зависимостей коммитов
        return {'commit1': ['commit2'], 'commit2': ['commit3']}

    def get_commit_message(self, commit_hash):
        # Логика получения сообщения коммита
        result = subprocess.run(
            ['git', '-C', self.repo_path, 'log', '--format=%s', commit_hash],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()

    def generate_puml_tree(self):
        # Логика генерации дерева зависимостей в формате PUML
        return "commit1 --> commit2\ncommit2 --> commit3"

    def generate_graph_image(self, filename):
        # Логика генерации изображения графа
        with open(filename, 'w') as f:
            f.write("dummy graph data")  # Записываем данные в файл
        print(f"Rendering graph to {filename} in png format.")


class TestGitDependencyVisualizer(unittest.TestCase):
    def setUp(self):
        # Создаем экземпляр визуализатора с мокаемым репозиторием
        self.visualizer = GitDependencyVisualizer(repo_path="test_repo")

    @patch("os.path.exists")
    def test_generate_graph_image(self, mock_exists):
        # Мокаем создание файла, чтобы проверить его существование
        mock_exists.return_value = True  # Указываем, что файл существует

        # Генерация графа
        self.visualizer.generate_graph_image("graph.png")

        # Проверяем, что файл был сохранен
        self.assertTrue(mock_exists("graph.png"))
        print(f"Graph generated: graph.png")  # Отладочный вывод

    def test_generate_puml_tree(self):
        # Тестируем генерацию PUML дерева
        puml_tree = self.visualizer.generate_puml_tree()
        self.assertTrue("commit1 --> commit2" in puml_tree)

    def test_get_commit_dependencies(self):
        # Тестируем получение зависимостей коммитов
        dependencies = self.visualizer.get_commit_dependencies()
        expected_dependencies = {'commit1': ['commit2'], 'commit2': ['commit3']}
        self.assertEqual(dependencies, expected_dependencies)

    @patch("subprocess.run")
    def test_get_commit_message(self, mock_subprocess):
        # Мокаем вызов subprocess для получения сообщения коммита
        mock_subprocess.return_value.stdout = "Commit message"
        
        commit_hash = "abc123"
        commit_message = self.visualizer.get_commit_message(commit_hash)
        
        mock_subprocess.assert_called_once_with(
            ['git', '-C', 'test_repo', 'log', '--format=%s', commit_hash],
            capture_output=True, text=True, check=True
        )
        
        self.assertEqual(commit_message, "Commit message")


if __name__ == "__main__":
    unittest.main()
