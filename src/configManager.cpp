#include "configManager.h"

ConfigManager::ConfigManager(QObject *parent) : QObject(parent), settings("Dancade", "Dancade")
{
}

// Getters
QString ConfigManager::getImagesPath() const { return settings.value("paths/images", "").toString(); }
QString ConfigManager::getVideosPath() const { return settings.value("paths/videos", "").toString(); }
QString ConfigManager::getMameExecutablePath() const { return settings.value("paths/mameExecutable", "").toString(); }
QString ConfigManager::getDisplayMode() const { return settings.value("settings/displayMode", "4-mix").toString(); }
QString ConfigManager::getSortingMode() const { return settings.value("settings/sorting", "alphabetical").toString(); }

// Setters
void ConfigManager::setImagesPath(const QString &path) { settings.setValue("paths/images", path); emit settingsChanged(); }
void ConfigManager::setVideosPath(const QString &path) { settings.setValue("paths/videos", path); emit settingsChanged(); }
void ConfigManager::setMameExecutablePath(const QString &path) { settings.setValue("paths/mameExecutable", path); emit settingsChanged(); }
void ConfigManager::setDisplayMode(const QString &mode) { settings.setValue("settings/displayMode", mode); emit settingsChanged(); }
void ConfigManager::setSortingMode(const QString &mode) { settings.setValue("settings/sorting", mode); emit settingsChanged(); }
