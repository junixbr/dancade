#ifndef CONFIGMANAGER_H
#define CONFIGMANAGER_H

#include <QObject>
#include <QSettings>

class ConfigManager : public QObject
{
    Q_OBJECT
public:
    explicit ConfigManager(QObject *parent = nullptr);
    
    // Getters
    QString getImagesPath() const;
    QString getVideosPath() const;
    QString getMameExecutablePath() const;
    QString getDisplayMode() const;
    QString getSortingMode() const;

    // Setters
    void setImagesPath(const QString &path);
    void setVideosPath(const QString &path);
    void setMameExecutablePath(const QString &path);
    void setDisplayMode(const QString &mode);
    void setSortingMode(const QString &mode);

signals:
    void settingsChanged();

private:
    QSettings settings;
};

#endif // CONFIGMANAGER_H
