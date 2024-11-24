import subprocess
import argparse
from pathlib import Path


class GitDependencyVisualizer:
    def __init__(self, repo_path, tag_name):
        self.repo_path = Path(repo_path).resolve()
        self.tag_name = tag_name
        self.dependencies = {}

    def get_commit_dependencies(self):
        """Собирает зависимости коммитов для указанного тега."""
        # Проверка наличия тега
        try:
            tag_commit = subprocess.run(
                ["git", "-C", str(self.repo_path), "rev-list", "-n", "1", self.tag_name],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Ошибка: Тег '{self.tag_name}' не найден в репозитории.") from e

        # Сбор коммитов и их родителей
        log_output = subprocess.run(
            ["git", "-C", str(self.repo_path), "log", "--graph", "--pretty=%H %P", tag_commit],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        for line in log_output.split("\n"):
            parts = line.split()
            commit = parts[0]
            parents = parts[1:]
            self.dependencies[commit] = parents

    def get_commit_message(self, commit_hash):
        """Возвращает описание коммита из git log."""
        log_output = subprocess.run(
            ["git", "-C", str(self.repo_path), "log", "--format=%s", commit_hash],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return log_output  # Возвращаем сообщение коммита

    def generate_puml_tree(self):
        """Генерирует код PlantUML для графа зависимостей с улучшенными названиями."""
        puml_lines = ["@startuml", "digraph G {"]

        for commit, parents in self.dependencies.items():
            commit_message = self.get_commit_message(commit)  # Получаем сообщение коммита
            puml_lines.append(f'    "{commit_message}" [label="{commit_message}"];')  # Используем сообщение как название
            for parent in parents:
                parent_message = self.get_commit_message(parent)  # Получаем сообщение родительского коммита
                puml_lines.append(f'    "{parent_message}" -> "{commit_message}" [color=black];')

        puml_lines.append("}")
        puml_lines.append("@enduml")
        return "\n".join(puml_lines)

    def visualize(self, plantuml_path, output_file="graph.png"):
        """Генерирует граф с помощью PlantUML."""
        puml_content = self.generate_puml_tree()
        puml_file = self.repo_path / "graph.puml"

        # Сохраняем PlantUML файл
        with open(puml_file, "w") as f:
            f.write(puml_content)

        # Вызов PlantUML
        subprocess.run(
            ["java", "-jar", plantuml_path, str(puml_file), "-o", str(self.repo_path)],
            check=True,
        )
        print(f"Граф зависимостей сохранен в {self.repo_path / output_file}")


def main():
    parser = argparse.ArgumentParser(description="Визуализация графа зависимостей Git-коммитов.")
    parser.add_argument("--repo", required=True, help="Путь к анализируемому репозиторию.")
    parser.add_argument("--tag", required=True, help="Имя тега.")
    parser.add_argument("--plantuml", required=True, help="Путь к программе PlantUML.")
    args = parser.parse_args()

    visualizer = GitDependencyVisualizer(args.repo, args.tag)
    visualizer.get_commit_dependencies()
    visualizer.visualize(args.plantuml)


if __name__ == "__main__":
    main()
