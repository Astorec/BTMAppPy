# Form implementation generated from reading ui file '/home/astorec/Documents/Repos/BeybladeTournamentManger/BTMPY/src/GUI/new_tournament.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_NewTournament(object):
    def setupUi(self, NewTournament):
        NewTournament.setObjectName("NewTournament")
        NewTournament.resize(442, 387)
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=NewTournament)
        self.buttonBox.setGeometry(QtCore.QRect(60, 340, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.name_text = QtWidgets.QTextEdit(parent=NewTournament)
        self.name_text.setGeometry(QtCore.QRect(40, 60, 371, 31))
        self.name_text.setObjectName("name_text")
        self.label = QtWidgets.QLabel(parent=NewTournament)
        self.label.setGeometry(QtCore.QRect(40, 40, 151, 20))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(parent=NewTournament)
        self.label_2.setGeometry(QtCore.QRect(40, 100, 101, 16))
        self.label_2.setObjectName("label_2")
        self.desc_text = QtWidgets.QTextEdit(parent=NewTournament)
        self.desc_text.setGeometry(QtCore.QRect(40, 130, 371, 121))
        self.desc_text.setObjectName("desc_text")
        self.type_cb = QtWidgets.QComboBox(parent=NewTournament)
        self.type_cb.setGeometry(QtCore.QRect(40, 280, 371, 24))
        self.type_cb.setObjectName("type_cb")
        self.type_cb.addItem("")
        self.type_cb.addItem("")
        self.type_cb.addItem("")
        self.type_cb.addItem("")
        self.type_cb.addItem("")
        self.type_cb.addItem("")
        self.label_3 = QtWidgets.QLabel(parent=NewTournament)
        self.label_3.setGeometry(QtCore.QRect(40, 260, 141, 16))
        self.label_3.setObjectName("label_3")

        self.retranslateUi(NewTournament)
        self.buttonBox.accepted.connect(NewTournament.accept) # type: ignore
        self.buttonBox.rejected.connect(NewTournament.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(NewTournament)

    def retranslateUi(self, NewTournament):
        _translate = QtCore.QCoreApplication.translate
        NewTournament.setWindowTitle(_translate("NewTournament", "Dialog"))
        self.label.setText(_translate("NewTournament", "Tournament Name"))
        self.label_2.setText(_translate("NewTournament", "Description"))
        self.type_cb.setItemText(0, _translate("NewTournament", "Single Elimination"))
        self.type_cb.setItemText(1, _translate("NewTournament", "Double Elimination"))
        self.type_cb.setItemText(2, _translate("NewTournament", "Round Robin"))
        self.type_cb.setItemText(3, _translate("NewTournament", "Swiss"))
        self.type_cb.setItemText(4, _translate("NewTournament", "Free For All"))
        self.type_cb.setItemText(5, _translate("NewTournament", "Leaderboard"))
        self.label_3.setText(_translate("NewTournament", "Tournament Type"))
