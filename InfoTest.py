import argparse
import requests
import re


# Функция для проверки URL-адреса на корректность
def validate_url(url):
    url_pattern = re.compile(
        r'^https://[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z]{2,5}$'
    )
    return bool(url_pattern.match(url))


# Функция для чтения URL-адресов из указанного файла
def read_hosts_from_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            hosts = [line.strip() for line in file if line.strip()]
            return hosts
    except FileNotFoundError:
        print(f"Ошибка: файл '{filename}' не найден")
        return []


# Функция для сохранения статистики в указанный файл
def save_results_to_file(filename, results):
    try:
        # w - запись с перезаписью файла
        with open(filename, 'w', encoding='utf-8') as file:
            file.write("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ\n")
            file.write("=" * 50 + "\n\n")

            for result in results:
                file.write(f"Host: {result['host']}\n")
                file.write(f"Success: {result['success']}\n")
                file.write(f"Failed: {result['failed']}\n")
                file.write(f"Errors: {result['errors']}\n")
                file.write(f"Min: {result['min']}\n")
                file.write(f"Max: {result['max']}\n")
                file.write(f"Avg: {result['avg']}\n")
                file.write("-" * 50 + "\n")

        print(f"Результаты сохранены в файл: {filename}")

    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")


# Функция тестирования хостов
def test_hosts(hosts, count):
    results = []

    for host in hosts:
        response_times = []
        success_count = 0
        failed_count = 0
        errors_count = 0

        for i in range(count):
            try:
                response = requests.get(host, timeout=1)

                # Успешный HTTP-запрос
                if 200 <= response.status_code < 400:
                    elapsed_time = response.elapsed.total_seconds()
                    response_times.append(elapsed_time)
                    success_count += 1

                # Ошибка сервера или клиента: 400/500 и выше
                else:
                    failed_count += 1

            except requests.exceptions.RequestException as e:
                errors_count += 1
                print(f"Ошибка при запросе к {host}: {e}")

        # Если были успешные запросы, рассчитываем статистику
        if response_times:
            min_time = min(response_times)
            max_time = max(response_times)
            avg_time = sum(response_times) / len(response_times)
        else:
            min_time = "N/A"
            max_time = "N/A"
            avg_time = "N/A"

        result = {
            'host': host,
            'success': success_count,
            'failed': failed_count,
            'errors': errors_count,
            'min': min_time,
            'max': max_time,
            'avg': avg_time
        }

        results.append(result)

    return results


# Создаём аргументы командной строки
parser = argparse.ArgumentParser(
    description='Тестирование доступности хостов'
)

parser.add_argument(
    '-H',
    '--hosts',
    help='URL адреса через запятую'
)

parser.add_argument(
    '-C',
    '--count',
    type=int,
    default=1,
    help='Количество запросов'
)

parser.add_argument(
    '-F',
    '--file',
    help='Путь до файла со списком адресов (по одному на строку)'
)

parser.add_argument(
    '-O',
    '--output',
    help='Путь до файла для сохранения результатов'
)


args = parser.parse_args()


# Проверяем, что указан только один из ключей -F или -H
if args.file and args.hosts:
    print("Ошибка: нельзя одновременно указывать -F и -H")
    exit(1)


# Проверяем, что указан хотя бы один из ключей -F или -H
if not args.file and not args.hosts:
    print("Ошибка: необходимо указать либо -F, либо -H")
    exit(1)


# Проверяем Count
if args.count <= 0:
    print("Ошибка: количество запросов должно быть положительным числом")
    exit(1)


if __name__ == '__main__':

    # Получаем список хостов
    hosts_list = []

    if args.file:
        hosts_list = read_hosts_from_file(args.file)
    else:
        hosts_list = [
            host.strip()
            for host in args.hosts.split(",")
        ]

    # Проверяем URL
    valid_hosts = []

    for host in hosts_list:
        if validate_url(host):
            valid_hosts.append(host)
        else:
            print(f"Предупреждение: некорректный URL: {host}")

    hosts_list = valid_hosts

    # Если после проверки не осталось адресов
    if not hosts_list:
        print("Ошибка: нет корректных URL для тестирования")
        exit(1)

    # Выполняем тестирование
    results = test_hosts(hosts_list, args.count)

    # Если указан -O, сохраняем результаты в файл
    if args.output:
        save_results_to_file(args.output, results)

    # Если -O не указан, выводим результаты в консоль
    else:
        print("\nРЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("=" * 50)

        for result in results:
            print(f"\nHost: {result['host']}")
            print(f"Success: {result['success']}")
            print(f"Failed: {result['failed']}")
            print(f"Errors: {result['errors']}")
            print(f"Min: {result['min']}")
            print(f"Max: {result['max']}")
            print(f"Avg: {result['avg']}")
            print("-" * 50)