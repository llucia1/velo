# ==============================================================================
# ETAPA 1: EXTRAER NODE.JS DE LA IMAGEN OFICIAL (Multi-stage)
# ==============================================================================
FROM node:22-bookworm-slim AS node_base

# ==============================================================================
# ETAPA 2: CONFIGURACIÓN DEL ENTORNO PHP RECOMENDADO PARA PRESTASHOP 9.1
# ==============================================================================
FROM php:8.4-fpm-bookworm

LABEL maintainer="josealbertollucia@gmail.com"

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Madrid

# ==============================================================================
# 1. DEPENDENCIAS DEL SISTEMA
# ==============================================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    unzip \
    zip \
    curl \
    wget \
    bash \
    libpng-dev \
    libjpeg62-turbo-dev \
    libfreetype6-dev \
    libwebp-dev \
    libzip-dev \
    libonig-dev \
    libicu-dev \
    libxml2-dev \
    g++ \
    libsodium-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# ==============================================================================
# 2. CONFIGURACIÓN Y COMPILACIÓN DE EXTENSIONES PHP
# ==============================================================================

RUN docker-php-ext-configure gd \
        --with-freetype \
        --with-jpeg \
        --with-webp

# json, iconv, dom, simplexml, xml, openssl, fileinfo, mbstring
# son built-in en PHP 8.4 — no necesitan instalación
RUN docker-php-ext-install -j$(nproc) \
    curl \
    gd \
    intl \
    pdo_mysql \
    zip \
    bcmath \
    opcache \
    sodium \
    sockets

# ==============================================================================
# 3. DIRECTIVAS DE CONFIGURACIÓN PHP (.ini)
# ==============================================================================
RUN { \
    echo 'memory_limit = 512M'; \
    echo 'max_input_vars = 5000'; \
    echo 'upload_max_filesize = 64M'; \
    echo 'post_max_size = 64M'; \
    echo 'max_execution_time = 300'; \
    echo 'date.timezone = Europe/Madrid'; \
    echo 'allow_url_fopen = On'; \
    echo 'allow_url_include = Off'; \
    echo 'expose_php = Off'; \
    echo 'curl.cainfo = /etc/ssl/certs/ca-certificates.crt'; \
    echo 'opcache.enable = 1'; \
    echo 'opcache.memory_consumption = 256'; \
    echo 'opcache.interned_strings_buffer = 16'; \
    echo 'opcache.max_accelerated_files = 20000'; \
    echo 'opcache.validate_timestamps = 1'; \
} > /usr/local/etc/php/conf.d/prestashop-defaults.ini

# ==============================================================================
# 4. ADMINISTRADOR DE DEPENDENCIAS (Composer)
# ==============================================================================
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# ==============================================================================
# 5. ENTORNO FRONT-END
# Copiamos todo el directorio de Node.js para mantener la estructura interna
# que npm necesita para resolver sus propios módulos
# ==============================================================================
COPY --from=node_base /usr/local /usr/local/node_runtime

ENV PATH="/usr/local/node_runtime/bin:$PATH"

# ==============================================================================
# 6. USUARIO DE EJECUCIÓN
# ==============================================================================
RUN useradd -u 1000 -m -s /bin/bash www-ps \
    && mkdir -p /var/www/html \
    && chown -R www-ps:www-ps /var/www/html

# ==============================================================================
# 7. VERIFICACIÓN EN BUILD TIME
# ==============================================================================
RUN php -r "extension_loaded('curl')      || die('FALTA ext-curl\n');"      && \
    php -r "extension_loaded('dom')       || die('FALTA ext-dom\n');"       && \
    php -r "extension_loaded('fileinfo')  || die('FALTA ext-fileinfo\n');"  && \
    php -r "extension_loaded('gd')        || die('FALTA ext-gd\n');"        && \
    php -r "extension_loaded('iconv')     || die('FALTA ext-iconv\n');"     && \
    php -r "extension_loaded('intl')      || die('FALTA ext-intl\n');"      && \
    php -r "extension_loaded('json')      || die('FALTA ext-json\n');"      && \
    php -r "extension_loaded('mbstring')  || die('FALTA ext-mbstring\n');"  && \
    php -r "extension_loaded('openssl')   || die('FALTA ext-openssl\n');"   && \
    php -r "extension_loaded('pdo_mysql') || die('FALTA ext-pdo_mysql\n');" && \
    php -r "extension_loaded('SimpleXML') || die('FALTA ext-SimpleXML\n');" && \
    php -r "extension_loaded('zip')       || die('FALTA ext-zip\n');"       && \
    php -r "extension_loaded('sodium')    || die('FALTA ext-sodium\n');"    && \
    php -r "extension_loaded('sockets')   || die('FALTA ext-sockets\n');"   && \
    php -r "in_array('opcache', get_loaded_extensions(true)) || die('FALTA ext-opcache\n');" && \
    node --version && npm --version && npx --version && composer --version  && \
    echo "=== Todas las extensiones verificadas OK ==="

# ==============================================================================
# 8. ENTORNO DE EJECUCIÓN
# ==============================================================================
WORKDIR /var/www/html

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD php-fpm -t || exit 1

USER www-ps

EXPOSE 9000
CMD ["php-fpm"]
