#include <QCoreApplication>
#include <QSettings>
#include <QStandardPaths>
#include <QDir>
#include <QDebug>

int main(int argc, char *argv[])
{
    QCoreApplication app(argc, argv);

    // Get the home directory
    QString configDir = QStandardPaths::writableLocation(QStandardPaths::HomeLocation) + "/.dancade";

    // Ensure the directory exists
    QDir dir(configDir);
    if (!dir.exists()) {
        dir.mkpath(".");
    }

    // Set up QSettings to use the custom config file
    QSettings settings(configDir + "/dancade.ini", QSettings::IniFormat);

    // Example: Save a test value (only the first time)
    if (!settings.contains("firstRun")) {
        settings.setValue("firstRun", true);
        settings.setValue("exampleSetting", "Hello, Dancade!");
    }

    if (settings.value("firstRun", true).toBool()) {
        settings.setValue("firstRun", false); // Mark as not first run

        // List contents of $HOME
        QDir homeDir(QStandardPaths::writableLocation(QStandardPaths::HomeLocation));
        QStringList homeContents = homeDir.entryList(QDir::AllEntries | QDir::NoDotAndDotDot);
        
        qDebug() << "Home directory contents:";
        for (const QString &file : homeContents) {
            qDebug() << file;
        }
    }

    // Read and print the stored value
    qDebug() << "Config file path:" << settings.fileName();
    qDebug() << "exampleSetting:" << settings.value("exampleSetting").toString();

    return app.exec();
}
