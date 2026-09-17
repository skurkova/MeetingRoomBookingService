import logging
import sys

import structlog


def setup_logging() -> None:
    """
    Инициализация структурированного асинхронного логирования.
    """

    # Базовые процессоры, применяемые ко всем записям
    shared_processors = [
        # Внедряет контекст запроса (user_id, request_id) во все логи
        structlog.contextvars.merge_contextvars,
        # Добавляет поле уровня логирования (info, warning, error)
        structlog.processors.add_log_level,
        # ISO-8601 формат времени для корректной сортировки логов
        structlog.processors.TimeStamper(fmt="iso"),
        # Автоматически форматирует traceback при возникновении исключений
        structlog.processors.format_exc_info,
    ]

    # Конфигурация structlog
    structlog.configure(
        # Адаптирует event_dict structlog для передачи в стандартный logging.Formatter
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        # AsyncBoundLogger выполняет запись логов в thread pool,
        # не блокируя asyncio event loop FastAPI
        wrapper_class=structlog.stdlib.AsyncBoundLogger,  # type: ignore[return-value]
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Кэширует экземпляр логгера для ускорения частых вызовов
        cache_logger_on_first_use=True,
    )

    # Форматтер для стандартной библиотеки logging.
    # foreign_pre_chain гарантирует, что логи от сторонних библиотек
    # также пройдут через shared_processors
    json_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        # Рендеринг события в JSON-строку
        processor=structlog.processors.JSONRenderer(),
    )

    # Обработчик вывода в стандартный поток (stdout).
    # Это обязательная практика для корректного сбора логов в Docker-контейнерах
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)

    # Применение настроек к корневому логгеру Python
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # Очищаем дефолтные хендлеры
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)

    # Очистка обработчиков ключевых библиотек и разрешение передачи логов
    # только корневому логгеру
    for logger_name in [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "sqlalchemy",
        "sqlalchemy.engine",
        "sqlalchemy.engine.Engine",
        "sqlalchemy.pool",
    ]:
        lib_logger = logging.getLogger(logger_name)
        lib_logger.handlers.clear()
        lib_logger.addHandler(console_handler)
        lib_logger.propagate = False


def get_logger(name: str) -> structlog.stdlib.AsyncBoundLogger:
    """
    Возвращает настроенный асинхронный логгер для конкретного модуля.
    """

    return structlog.get_logger(name)  # type: ignore[return-value]
