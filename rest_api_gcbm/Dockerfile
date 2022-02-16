# GCBM build taken from:
# https://github.com/moja-global/moja.canada/blob/develop/Files/Dockerfile

# We'd like to replace this with a pre-built container
# But for now, let's start from scratch

# Stage 1 - base image with Poco, GDAL and Zipper
FROM ubuntu:bionic AS base

ARG NUM_CPU=16
ARG DEBIAN_FRONTEND=noninteractive

ENV ROOTDIR /usr/local
ENV GDAL_VERSION 2.4.1
ENV CMAKE_VERSION 3.15.0
ENV POCO_VERSION 1.9.2
ENV BOOST_VERSION 1_72_0
ENV BOOST_VERSION_DOT 1.72.0
ENV FMT_VERSION 6.1.2
ENV SQLITE_VERSION 3.31.1

WORKDIR $ROOTDIR/

# Install basic dependencies - add ODBC for GCBM
RUN apt-get update -y && apt-get install -y --fix-missing --no-install-recommends \
    software-properties-common build-essential ca-certificates \
    libtool automake zlib1g-dev libspatialite-dev pkg-config libsqlite3-dev sqlite3 \
	  python3-dev python3-numpy python3-pip openssl libssl-dev libpq-dev \
    libcurl4-gnutls-dev libproj-dev libxml2-dev libexpat-dev libxerces-c-dev \
    libgeos-dev libpoppler-dev \
    git wget bash-completion nasm \
    postgresql-client-10 postgresql-server-dev-10 \
    unixodbc unixodbc-dev \
  && apt-get -y autoremove \
	&& 	apt-get clean

# set environment variables
ENV PATH $ROOTDIR/bin:$PATH
ENV LD_LIBRARY_PATH $ROOTDIR/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH $ROOTDIR/lib:$PYTHONPATH

WORKDIR $ROOTDIR/src

RUN wget https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}.tar.gz \
    && tar xzf cmake-${CMAKE_VERSION}.tar.gz \
    && cd cmake-${CMAKE_VERSION} \
    && ./bootstrap --system-curl --parallel=$NUM_CPU \
	&& make --quiet install \
	&& make clean \
    && cd ..

# ODBC enabled for GCBM
RUN wget https://pocoproject.org/releases/poco-${POCO_VERSION}/poco-${POCO_VERSION}-all.tar.gz \
    && tar -xzf poco-${POCO_VERSION}-all.tar.gz && mkdir poco-${POCO_VERSION}-all/cmake-build && cd poco-${POCO_VERSION}-all/cmake-build \
    && cmake -DCMAKE_BUILD_TYPE=$BUILD_TYPE -DCMAKE_INSTALL_PREFIX=$ROOTDIR \
            -DPOCO_UNBUNDLED=ON \
            -DPOCO_STATIC=OFF \
            -DENABLE_ENCODINGS=OFF \
            -DENABLE_ENCODINGS_COMPILER=OFF \
            -DENABLE_XML=OFF \
            -DENABLE_JSON=ON \
            -DENABLE_MONGODB=OFF \
            -DENABLE_REDIS=OFF \
            -DENABLE_PDF=OFF \
            -DENABLE_UTIL=OFF \
            -DENABLE_NET=OFF \
            -DENABLE_NETSSL=OFF \
            -DENABLE_CRYPTO=OFF \
            -DENABLE_DATA=ON \
            -DENABLE_DATA_SQLITE=ON \
            -DENABLE_DATA_MYSQL=OFF \
            -DENABLE_DATA_ODBC=ON \
            -DENABLE_SEVENZIP=OFF \
            -DENABLE_ZIP=OFF \
            -DENABLE_PAGECOMPILER=OFF \
            -DENABLE_PAGECOMPILER_FILE2PAGE=OFF \
            -DENABLE_TESTS:BOOL=OFF .. \
	&& make --quiet -j $NUM_CPU \
    && make --quiet install/strip \
    && make clean \
    && cd $ROOTDIR/src
# build user-config.jam files
RUN echo "using python : 3.6 : /usr ;" > ~/user-config.jam

RUN	git clone --recursive https://github.com/sebastiandev/zipper.git \
	&& cd zipper && git checkout e9f150516cb55d194b5e01d21a9527783e98311d && mkdir build  && cd build \
	&& cmake .. \
	&& make --quiet -j $NUM_CPU \
    && make --quiet install \
    && make clean \
    && cd $ROOTDIR/src

RUN wget https://boostorg.jfrog.io/artifactory/main/release/${BOOST_VERSION_DOT}/source/boost_${BOOST_VERSION}.tar.bz2 \
    && tar --bzip2 -xf boost_${BOOST_VERSION}.tar.bz2 && cd boost_${BOOST_VERSION}  \
    && ./bootstrap.sh --prefix=$ROOTDIR \
    && ./b2 -d0 -j $NUM_CPU cxxstd=14 install variant=release link=shared  \
    && ./b2 clean \
    && cd $ROOTDIR/src

RUN wget https://github.com/fmtlib/fmt/archive/${FMT_VERSION}.tar.gz \
    && mkdir libfmt-${FMT_VERSION} && tar -xzf ${FMT_VERSION}.tar.gz -C libfmt-${FMT_VERSION} --strip-components=1 &&  cd libfmt-${FMT_VERSION} \
    && cmake -G"Unix Makefiles" -DCMAKE_BUILD_TYPE=RELEASE -DCMAKE_INSTALL_PREFIX=$ROOTDIR \
            -DFMT_DOC=OFF \
            -DFMT_TEST=OFF . \
    && make --quiet -j $NUM_CPU install/strip \
    && make clean \
    && cd $ROOTDIR/src

RUN wget http://download.osgeo.org/gdal/${GDAL_VERSION}/gdal-${GDAL_VERSION}.tar.gz \
    && tar -xvf gdal-${GDAL_VERSION}.tar.gz && cd gdal-${GDAL_VERSION} \
    && ./configure  --without-libtool --with-hide-internal-symbols \
        --with-python --with-spatialite --with-pg --with-curl --prefix=$ROOTDIR \
        --with-libtiff=internal --with-rename-internal-libtiff-symbols \
        --with-geotiff=internal --with-rename-internal-libgeotiff-symbols \
    && make --quiet -j $NUM_CPU \
    && make install \
    && make clean \
    && cd $ROOTDIR/src

RUN strip -s $ROOTDIR/lib/libgdal.so
RUN for i in $ROOTDIR/lib/python3/dist-packages/osgeo/*.so; do strip -s $i 2>/dev/null || /bin/true; done
RUN strip -s $ROOTDIR/bin/gdal_contour && strip -s $ROOTDIR/bin/gdal_grid \
    && strip -s $ROOTDIR/bin/gdal_rasterize && strip -s $ROOTDIR/bin/gdal_translate && strip -s $ROOTDIR/bin/gdaladdo \
    && strip -s $ROOTDIR/bin/gdalbuildvrt && strip -s $ROOTDIR/bin/gdaldem && strip -s $ROOTDIR/bin/gdalenhance \
    && strip -s $ROOTDIR/bin/gdalinfo && strip -s $ROOTDIR/bin/gdallocationinfo && strip -s $ROOTDIR/bin/gdalmanage \
    && strip -s $ROOTDIR/bin/gdalserver && strip -s $ROOTDIR/bin/gdalsrsinfo && strip -s $ROOTDIR/bin/gdaltindex \
    && strip -s $ROOTDIR/bin/gdaltransform && strip -s $ROOTDIR/bin/gdalwarp && strip -s $ROOTDIR/bin/gnmanalyse \
    && strip -s $ROOTDIR/bin/gnmmanage && strip -s $ROOTDIR/bin/nearblack && strip -s $ROOTDIR/bin/ogr2ogr \
    && strip -s $ROOTDIR/bin/ogrinfo && strip -s $ROOTDIR/bin/ogrlineref && strip -s $ROOTDIR/bin/ogrtindex \
    && strip -s $ROOTDIR/bin/testepsg

ENV CURL_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt
ENV GDAL_DATA=/usr/local/share/gdal
ENV GDAL_HTTP_VERSION 2

RUN apt-get update -y \
    && apt-get remove -y --purge build-essential \
    && cd $ROOTDIR/src/gdal-${GDAL_VERSION}/swig/python \
    && python3 setup.py build \
    && python3 setup.py install

RUN ldconfig
RUN rm -r $ROOTDIR/src/*


## Stage 2 - build FLINT
FROM base AS flint

ARG NUM_CPU=16
ARG DEBIAN_FRONTEND=noninteractive
ARG BUILD_TYPE=RELEASE

ENV ROOTDIR /usr/local

WORKDIR $ROOTDIR/src

# set environment variables
ENV PATH $ROOTDIR/bin:$PATH
ENV LD_LIBRARY_PATH $ROOTDIR/lib:$ROOTDIR/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ENV PYTHONPATH $ROOTDIR/lib:$PYTHONPATH
ENV CURL_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt
ENV GDAL_DATA=/usr/local/share/gdal
ENV GDAL_HTTP_VERSION 2
ENV GDAL_HTTP_MERGE_CONSECUTIVE_RANGES YES
ENV GDAL_HTTP_MULTIPLEX YES

# hardcoded to develop
RUN git clone --recursive --depth 1 -b develop https://github.com/moja-global/FLINT.git flint \
    && mkdir -p flint/Source/build && cd flint/Source/build \
    && cmake -DCMAKE_BUILD_TYPE=$BUILD_TYPE  \
            -DCMAKE_INSTALL_PREFIX=$ROOTDIR \
            -DENABLE_TESTS:BOOL=OFF \
            -DENABLE_MOJA.MODULES.GDAL=ON \
            -DENABLE_MOJA.MODULES.ZIPPER=ON \
            -DENABLE_MOJA.MODULES.LIBPQ=ON \
            -DBoost_USE_STATIC_LIBS=OFF \
            -DBUILD_SHARED_LIBS=ON .. \
	&& make --quiet -j $NUM_CPU \
	&& make --quiet install \
    && cd $ROOTDIR/src

RUN ln -s $ROOTDIR/lib/libmoja.modules.* $ROOTDIR/bin

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN pip3 install setuptools
RUN git clone --recursive --depth 1 -b develop  https://github.com/moja-global/FLINT.data.git FLINT.data \
    && cd FLINT.data \
    && pip3 install .

RUN rm -Rf $ROOTDIR/src/* \
    && ldconfig

RUN useradd -ms /bin/bash moja
USER moja
WORKDIR /home/moja


## Stage 3 - GCBM
FROM flint AS gcbm

ARG NUM_CPU=14
ARG BUILD_TYPE=RELEASE

ENV DEBIAN_FRONTEND=noninteractive
USER root

# set environment variables
ENV ROOTDIR /usr/local/
WORKDIR $ROOTDIR/

ENV PATH $ROOTDIR/bin:$PATH
ENV POCO_VERSION 1.9.2
ENV LD_LIBRARY_PATH $ROOTDIR/lib:$ROOTDIR/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ENV PYTHONPATH $ROOTDIR/lib:$PYTHONPATH
ENV CURL_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt
ENV GDAL_DATA=/usr/local/share/gdal
ENV GDAL_HTTP_VERSION 2
ENV GDAL_HTTP_MERGE_CONSECUTIVE_RANGES YES
ENV GDAL_HTTP_MULTIPLEX YES

RUN apt-get install -y doxygen doxygen-latex graphviz postgis

# moja.canada requires libpqxx.
WORKDIR /tmp
RUN git clone --recursive https://github.com/jtv/libpqxx.git \
    && cd libpqxx \
    && mkdir build \
    && cd build \
    && cmake -DCMAKE_BUILD_TYPE=$BUILD_TYPE -DCMAKE_INSTALL_PREFIX=/usr/local/ \
        -DSKIP_BUILD_TEST=ON \
        -FSKIP_PQXX_STATIC=ON .. \
        -DCMAKE_CXX_FLAGS=-fPIC \
        -DPostgreSQL_TYPE_INCLUDE_DIR=/usr/include/postgresql/ \
    && make --quiet -j $NUM_CPU install/strip \
    && make clean

# moja.canada
RUN cd $ROOTDIR/src && git clone -b develop https://github.com/moja-global/moja.canada

WORKDIR $ROOTDIR/src/moja.canada/Source/build
RUN cmake -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
           -DCMAKE_INSTALL_PREFIX=/usr/local \
           -DENABLE_TESTS:BOOL=OFF \
           -DPostgreSQL_TYPE_INCLUDE_DIR=/usr/include/postgresql/ \
           .. \
    && make --quiet -s -j $NUM_CPU \
    && make --quiet install \
    && make clean

WORKDIR $ROOTDIR/src
RUN mkdir -p /opt/gcbm
RUN ln -t /opt/gcbm /usr/local/lib/lib*
RUN ln -t /opt/gcbm /usr/local/bin/moja.cli


# TODO: replace with a pre-build container
# FROM ghcr.io/moja-global/gcbm
FROM gcbm AS gcbm-cloud
WORKDIR /app

RUN set -xe \
    && apt-get update \
    && apt-get install -y python-pip
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt
ENV PORT 8080

COPY . .

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
