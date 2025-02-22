QT += core gui quick multimedia
CONFIG += c++11

TARGET = Dancade
TEMPLATE = app

# Include directories
INCLUDEPATH += include

# Source and header files
SOURCES += src/main.cpp \
           src/configManager.cpp \
           src/mediaPlayer.cpp

HEADERS += include/configManager.h \
           include/mediaPlayer.h

# QML files and resources
RESOURCES += qml/resources.qrc

# Translation files for multi-language support
# English is the default language; add other translations as needed.
TRANSLATIONS = translations/dancade_en.ts \
               translations/dancade_pt.ts
