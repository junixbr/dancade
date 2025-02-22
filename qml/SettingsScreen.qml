import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    id: settingsWindow
    visible: true
    width: 600
    height: 400
    title: qsTr("Settings")

    Column {
        anchors.centerIn: parent
        spacing: 20

        Label { text: qsTr("Images Path:") }
        TextField {
            id: imagesPathField
            width: 300
            text: configManager.getImagesPath()
            onEditingFinished: configManager.setImagesPath(text)
        }

        Label { text: qsTr("Videos Path:") }
        TextField {
            id: videosPathField
            width: 300
            text: configManager.getVideosPath()
            onEditingFinished: configManager.setVideosPath(text)
        }

        Label { text: qsTr("MAME Executable Path:") }
        TextField {
            id: mamePathField
            width: 300
            text: configManager.getMameExecutablePath()
            onEditingFinished: configManager.setMameExecutablePath(text)
        }

        Label { text: qsTr("Display Mode:") }
        ComboBox {
            id: displayModeBox
            width: 300
            model: ["4-mix", "screenshot", "title screenshot", "vertical poster"]
            currentIndex: model.indexOf(configManager.getDisplayMode())
            onActivated: configManager.setDisplayMode(currentText)
        }

        Label { text: qsTr("Sorting Mode:") }
        ComboBox {
            id: sortingBox
            width: 300
            model: ["alphabetical", "rating"]
            currentIndex: model.indexOf(configManager.getSortingMode())
            onActivated: configManager.setSortingMode(currentText)
        }

        Button {
            text: qsTr("Close")
            onClicked: settingsWindow.close()
        }
    }
}
