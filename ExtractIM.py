import os
import sys
import time
import re
import shutil
import random
from pathlib import Path
from functools import partial

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QMessageBox, QTableWidget, \
    QTableWidgetItem, QHeaderView, QCheckBox, QLineEdit
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QDateTime, Qt
from PIL import Image, ImageQt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('D:\\Programming\\ExtractIm\\ExtractIm.ui', self)

        self.setWindowTitle("ImportIM v1.5 - 17/01/2025")
        self.showMaximized()  # Set the window to maximized
        self.setWindowIcon(QIcon("icon.png"))

        self.label = self.findChild(QLabel, 'label')
        self.label.setStyleSheet("color: red;")
        self.label_target = self.findChild(QLabel, 'label_target')
        self.label_target.setStyleSheet("color: red;")
        self.label_info = self.findChild(QLabel,'label_info')

        self.image_label = self.findChild(QLabel, 'image_label')
        self.image_label.setStyleSheet("border: 2px solid black;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_totalfichiers = self.findChild(QLabel,'label_totalfichiers')
        self.label_totalrepertoires = self.findChild(QLabel,'label_totalrepertoires')
        self.label_CurrentImage = self.findChild(QLabel,'label_CurrentImage')
        self.label_TotalImage = self.findChild(QLabel,'label_TotalImage')

        self.lineEditRepSource=self.findChild(QLineEdit,'lineEditRepSource')

        self.checkBoxCopyorMove=self.findChild(QCheckBox,'checkBoxCopyorMove')

        self.button_select = self.findChild(QPushButton, 'button_select')
        self.button_select.clicked.connect(self.select_directory)
        self.button_select_target = self.findChild(QPushButton, 'button_select_target')
        self.button_select_target.clicked.connect(self.select_directory_target)
        self.button_quit = self.findChild(QPushButton, 'button_quit')
        self.button_quit.clicked.connect(self.quit_application)
        self.pushButtonStart=self.findChild(QPushButton,'pushButtonStart')
        self.pushButtonStart.clicked.connect(self.start)
        self.pushButtonStart.setStyleSheet("background-color: lightblue; color: black; font-size: 14px;")
        self.pushButtonGarder=self.findChild(QPushButton,'pushButtonGarder')
        self.pushButtonGarder.setEnabled(False)
        self.pushButtonGarder.clicked.connect(self.garder)
        self.pushButtonSupprimer=self.findChild(QPushButton,'pushButtonSupprimer')
        self.pushButtonSupprimer.setEnabled(False)
        self.pushButtonSupprimer.clicked.connect(self.supprimer)
        self.pushButtonRenommer=self.findChild(QPushButton,'pushButtonRenommer')
        self.pushButtonRenommer.clicked.connect(self.renommer)
        self.pushButtonRenommer.setStyleSheet("background-color: lightblue; color: black; font-size: 14px;")
        self.pushButtonSuivant=self.findChild(QPushButton,'pushButtonSuivant')
        self.pushButtonSuivant.clicked.connect(self.suivant)
        self.pushButtonPrecedent=self.findChild(QPushButton,'pushButtonPrecedent')
        self.pushButtonPrecedent.clicked.connect(self.precedent)
        self.pushButtonRepertoireValider=self.findChild(QPushButton,'pushButtonRepertoireValider')
        self.pushButtonRepertoireValider.clicked.connect(self.valider)
        self.pushButton90G=self.findChild(QPushButton,'pushButton90G')
        self.pushButton90G.setEnabled(False)
        self.pushButton90G.clicked.connect(partial(self.rotation,90))
        self.pushButton90D=self.findChild(QPushButton,'pushButton90D')
        self.pushButton90D.setEnabled(False)
        self.pushButton90D.clicked.connect(partial(self.rotation,-90))
        self.pushButtonNormal=self.findChild(QPushButton,'pushButtonNormal')
        self.pushButtonNormal.setEnabled(False)
        self.pushButtonNormal.clicked.connect(partial(self.rotation,0))
        self.pushButton180=self.findChild(QPushButton,'pushButton180')
        self.pushButton180.setEnabled(False)
        self.pushButton180.clicked.connect(partial(self.rotation,180))

        self.table_widget = self.findChild(QTableWidget, 'table_widget')
        self.table_widget.currentCellChanged.connect(self.display_image)
 

        # Variables
        self.activer_renommer=False
        self.image_renommer=""
        self.repertoire_renommer=""
        self.index_renommer=0
        self.nb_images_renommer = 0
        # Rotation
        self.rotated_image=None

        # UNIQUEMENT POUR LES TESTS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.default_directory_source="C:/Users/Admin/Desktop/Tri"
        self.default_directory_target="D:/Test"


    def rotation(self,angle):
        # Récupérer la ligne actuellement sélectionnée
        current_row = self.table_widget.currentRow()
        if current_row != -1:
            print(f"Ligne sélectionnée: {current_row}")
            file_path = self.table_widget.item(current_row, 3).text()
            file_name = self.table_widget.item(current_row, 0).text()
            file_full_path=file_path+"/"+file_name
            # Charger l'image avec Pillow
            try:
                # Charger l'image avec Pillow
                image = Image.open(file_full_path)

                # Effectuer une rotation de 90 degrés vers la droite
                self.rotated_image = image.rotate(angle, expand=True)

                # Convertir l'image Pillow en QImage
                qimage = ImageQt.ImageQt(self.rotated_image)

                # Convertir QImage en QPixmap
                qpixmap = QPixmap.fromImage(qimage)

                # Vérifier si qpixmap est valide
                if qpixmap.isNull():
                    print("Erreur : Impossible de charger l'image.")
                    return

                # Redimensionner l'image tout en conservant le ratio d'aspect
                scaled_pixmap_preview = qpixmap.scaled(900, 600, Qt.AspectRatioMode.KeepAspectRatio)

                # Afficher l'image dans le label
                self.image_label.setPixmap(scaled_pixmap_preview)

                # Sauvegarder l'image rotée
                #rotated_image_path = "rotated_" + image_path
                #rotated_image.save(rotated_image_path)
            except Exception as e:
                print(f"Une erreur s'est produite : {e}")


    def valider(self):
        # Rename the directory
        print('repertoire_renommer' + self.repertoire_renommer)
        rep_source=self.repertoire_renommer
        rep_dest=os.path.dirname(rep_source)+"/"+self.lineEditRepSource.text()
        print('rep_source'+rep_source)
        print('rep_dest' + rep_dest)
        os.rename( rep_source,rep_dest)
        self.repertoire_renommer = ""
        self.index_renommer = 0
        self.renommer()

    def suivant(self):
        #print("Suivant->"+str(self.index_renommer))
        #print("nb_images_renommer"+str(self.nb_images_renommer))
        if (self.index_renommer < self.nb_images_renommer-1):
            self.index_renommer=self.index_renommer+1
            #print("self.repertoire_renommer"+self.repertoire_renommer)
            self.table_widget.selectRow(self.index_renommer)
            self.renommer()

    def precedent(self):
        #print("Precedent->"+str(self.index_renommer))
        #print("nb_images_renommer"+str(self.nb_images_renommer))
        if (self.index_renommer != 0):
            self.index_renommer=self.index_renommer-1
            #print(self.index_renommer)
            self.table_widget.selectRow(self.index_renommer)
            self.renommer()

    def supprimer(self):
        fichier_source = self.get_filename_cell_value()
        chemin_source = self.get_path_cell_value()
        file_full_path_source = chemin_source + "/" + fichier_source

        confirm_msg = QMessageBox()
        confirm_msg.setIcon(QMessageBox.Icon.Warning)
        confirm_msg.setText(f"Voulez-vous vraiment supprimer le fichier {fichier_source} ?")
        confirm_msg.setWindowTitle("Confirmer la suppression")
        confirm_msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        ret = confirm_msg.exec()

        if ret == QMessageBox.StandardButton.Yes:
            print(f"Fichier {fichier_source} supprimé.")
            os.remove(file_full_path_source)  # Delete the file

            # On supprimer la premiere ligne du tableau
            self.supprimer_premiere_ligne()

            # On affiche la premiere image de la ligne si elle existe
            if self.table_widget.rowCount() > 0:
                self.start()
            else:
                self.rafraichir_nb_lignes_tableau()
                self.image_label.clear()
                self.show_message("INFO", "Terminé !")

        self.start()

    def renommer(self):
        if (self.label_target.text() == "Aucun répertoire destination sélectionné"):
            self.show_message("ERREUR", "Aucun répertoire destination sélectionné !")
            return

        self.activer_renommer=True

        # Définir le chemin de départ
        directory_path = self.label_target.text()
        start_path = Path(directory_path)

        # Définir le motif regex pour le format yyyy-mm-dd
        pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')

        # Lancer la recherche
        results=[]
        self.find_directories(start_path,results,pattern)
        nombre=len(results)
        if nombre > 0:
            self.label_totalrepertoires.setText(str(nombre))
            for result in results:
                last_directory = os.path.basename(result)
                print(last_directory)
                print(self.index_renommer)
                image_files = self.list_image_files(result)
                self.nb_images_renommer=len(image_files)
                self.label_TotalImage.setText(str(self.nb_images_renommer))
                if len(image_files) > 0 and (len(image_files) > self.index_renommer):
                    self.repertoire_renommer = image_files[self.index_renommer][3]
                    #print("image file index ="+image_files[self.index_renommer])
                    self.afficher_image_label(image_files[self.index_renommer][3]+"\\"+image_files[self.index_renommer][0])
                    self.label_CurrentImage.setText(str(self.index_renommer+1))
                    self.lineEditRepSource.setText(last_directory)
                self.table_widget.selectRow(self.index_renommer)
                break
        else:
            self.label_info.setText("Plus de répertoire à renommer !")
            self.index_renommer=0
            self.label_totalrepertoires.setText("0")


    def afficher_image_label(self,image):
        pixmap = QPixmap(image)
        scaled_pixmap_preview = pixmap.scaled(900, 600, Qt.AspectRatioMode.KeepAspectRatio)
        # Display the image in the right layout
        self.image_label.setPixmap(scaled_pixmap_preview)

    # Fonction pour rechercher récursivement les répertoires
    def find_directories(self,path,results,pattern):
        for item in path.iterdir():
            if item.is_dir():
                if pattern.match(item.name):
                    results.append(item)
                self.find_directories(item,results,pattern)

    def creer_emplacement(self):
        directory_path=self.label_target.text()

        fichier_source = self.get_filename_cell_value()
        chemin_source = self.get_path_cell_value()
        file_full_path_source = chemin_source + "/" + fichier_source
        file_target=os.path.basename(fichier_source)
        print("fichier actuel"+file_full_path_source)
        # Récupérer les informations de création du fichier
        #creation_time = os.path.getctime(file_full_path_source)
        # Récupérer les informations de modification du fichier
        creation_time = os.path.getmtime(file_full_path_source)

        # Convertir le temps en format lisible
        creation_date = time.localtime(creation_time)

        # Extraire l'année, le mois et le jour
        creation_year = str(creation_date.tm_year)
        creation_month = str(creation_date.tm_mon).zfill(2)
        creation_day = str(creation_date.tm_mday).zfill(2)
        target_full_path=directory_path+"/"+creation_year+"/"+creation_year+"-"+creation_month+"-"+creation_day
        print("target_full_path" + target_full_path)
        # Vérifier si le répertoire existe
        if not os.path.exists(directory_path+"/"+creation_year):
            os.makedirs(directory_path+"/"+creation_year)
        if not os.path.exists(target_full_path):
            os.makedirs(target_full_path)

        return (file_full_path_source,target_full_path+"/"+file_target)

    def files_are_identical(self,fichier1, fichier2):
        # Vérifier la taille des fichiers
        print(fichier1)
        print(fichier2)

        if os.path.getsize(fichier1) != os.path.getsize(fichier2):
            return False

        # Vérifier le contenu des fichiers
        with open(fichier1, 'rb') as f1, open(fichier2, 'rb') as f2:
            if f1.read() != f2.read():
                print("2")
                return False

        # Vérifier les dates de modification des fichiers
        if os.path.getmtime(fichier2) != os.path.getmtime(fichier2):
            return False

        return True


    def copy_move(self,file_full_path_source, target_full_path):
        # Même nom de fichier ?
        #if (os.path.basename(file_full_path_source) == os.path.basename(target_full_path)):
        if os.path.exists(target_full_path):
            if (not self.files_are_identical(file_full_path_source,target_full_path)):
                print("3")
                random_number = random.randint(1, 999)
                file_name = os.path.basename(file_full_path_source)
                target_dir_name=os.path.dirname(target_full_path)
                file_name2 = Path(target_full_path)
                file_extension = file_name2.suffix
                file_name = file_name2.stem
                target_full_path = target_dir_name + "/" + file_name + "_" + str(random_number) + file_extension
                self.label_info.setText('Fichier avec le même nom mais différent déjà existant : renommé '+file_name + "_" + str(random_number) + file_extension+'!')
            else:
                self.label_info.setText('Fichier strictiquement identique déjà existant !')

        # copie ou move ?
        print(file_full_path_source)
        print(target_full_path)
        if self.checkBoxCopyorMove.isChecked():
            if self.rotated_image != None:
                self.rotated_image.save(target_full_path)
            else:
                shutil.copy2(file_full_path_source, target_full_path)
            self.label_info.setText("Copie de l'image réalisée !")
        else:
            shutil.move(file_full_path_source, target_full_path)
            if self.rotated_image != None:
                self.rotated_image.save(target_full_path)
            self.label_info.setText("Déplacement de l'image faite !")

        # Reinit
        self.rotated_image=None


    def garder(self):
        self.label_info.setText('')

        # Creation des repertoires cibles
        file_full_path_source,target_full_path=self.creer_emplacement()
        # Move ou copy
        print(file_full_path_source)
        print(target_full_path)
        self.copy_move(file_full_path_source,target_full_path)
        print("move ou copy fait")

        # On supprimer la premiere ligne du tableau
        self.supprimer_premiere_ligne()
        print("suppression premiere line faite")

        # On propose le renommage du répertoire
        directory_target = os.path.dirname(target_full_path)
        self.lineEditRepSource.setText(directory_target)

        # On affiche la premiere image de la ligne si elle existe
        if self.table_widget.rowCount() > 0:
            self.start()
        else:
            self.rafraichir_nb_lignes_tableau()
            self.image_label.clear()
            self.show_message("INFO", "Terminé !")




    def start(self):
        # Vérifications
        if (self.label.text() == "Aucun répertoire source sélectionné"):
            self.show_message("ERREUR","Aucun répertoire source sélectionné !")
            return
        if not os.path.isdir(self.label.text()):
            self.show_message("ERREUR", "Le répertoire source n'existe pas !")
            return
        if (self.label_target.text() == "Aucun répertoire destination sélectionné"):
            self.show_message("ERREUR", "Aucun répertoire destination sélectionné !")
            return
        if not os.path.isdir(self.label_target.text()):
            self.show_message("ERREUR", "Le répertoire destination n'existe pas !")
            return
        fichier=self.get_filename_cell_value()
        chemin=self.get_path_cell_value()
        file_full_path=chemin+"/"+fichier
        if os.path.isfile(file_full_path) and file_full_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            pixmap = QPixmap(file_full_path)
            scaled_pixmap_preview = pixmap.scaled(900, 600, Qt.AspectRatioMode.KeepAspectRatio)
            # Display the image in the right layout
            self.image_label.setPixmap(scaled_pixmap_preview)
        self.rafraichir_nb_lignes_tableau()

        # Select the first row if totalfile > 0
        if int(self.label_totalfichiers.text()) > 0:
            self.table_widget.setCurrentCell(0, 0)
            #self.table_widget.cellClicked.emit(0, 0)

        # Activer les boutons
        self.pushButtonGarder.setEnabled(True)
        self.pushButtonSupprimer.setEnabled(True)
        self.pushButton90G.setEnabled(True)
        self.pushButton90D.setEnabled(True)
        self.pushButtonNormal.setEnabled(True)
        self.pushButton180.setEnabled(True)
        self.pushButtonGarder.setStyleSheet("background-color: green; color: white; font-size: 14px;")
        self.pushButtonSupprimer.setStyleSheet("background-color: red; color: white; font-size: 14px;")

    def list_image_files(self,directory):
        # Définir la liste des extensions de fichiers image
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']

        # Initialiser une liste vide pour stocker les noms complets des fichiers image
        image_files = []

        # Parcourir le répertoire
        for root, dirs, files in os.walk(directory):
            for file in files:
                # Vérifier si le fichier a une des extensions d'image
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    # Ajouter le chemin complet du fichier image à la liste
                    #image_files.append(os.path.join(root, file))
                    full_path = os.path.join(root, file)
                    file_path = os.path.dirname(full_path)
                    # En Mo
                    file_size_megabytes = os.path.getsize(full_path)/ (1024 * 1024)
                    file_size=f"{file_size_megabytes:.2f} Mo"
                        # creation
                        #creation_time = QDateTime.fromSecsSinceEpoch(int(os.path.getctime(full_path))).toString()
                        # Modification
                    creation_time = QDateTime.fromSecsSinceEpoch(int(os.path.getmtime(full_path))).toString()
                        
                    image_files.append((file,file_size,creation_time,file_path))

        # Set table dimensions
        self.table_widget.setRowCount(len(image_files))
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Name", "Size","Modification Time","Path"])

        # Populate table with file information
        for row, (file_name,file_size,creation_time,file_path) in enumerate(image_files):
            self.table_widget.setItem(row, 0, QTableWidgetItem(file_name))
            self.table_widget.setItem(row, 1, QTableWidgetItem(file_size))
            self.table_widget.setItem(row, 2, QTableWidgetItem(creation_time))
            self.table_widget.setItem(row, 3, QTableWidgetItem(file_path))

        # Adjust column widths to fit content
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Select the first row if totalfile > 0
        #if len(image_files) > 0:
        #    self.table_widget.setCurrentCell(0, 0)

        return image_files

    def select_directory(self):
        dir_name = QFileDialog.getExistingDirectory(self, "Sélectionner le répertoire source",self.default_directory_source)
        if dir_name:
            self.label.setText(f"{dir_name}")
            self.analyze_directory(dir_name)

        # Select the first row if totalfile > 0
        if int(self.label_totalfichiers.text()) > 0:
            self.table_widget.setCurrentCell(0, 0)
            #self.table_widget.cellClicked.emit(0, 0)


    def select_directory_target(self):
        dir_name_target = QFileDialog.getExistingDirectory(self, "Sélectionner le répertoire destination",self.default_directory_target)
        if dir_name_target:
            self.label_target.setText(f"{dir_name_target}")

    def get_filename_cell_value(self):
        item = self.table_widget.item(0, 0)
        if item is not None:
            return item.text()
        else:
            return None

    def get_path_cell_value(self):
        item = self.table_widget.item(0, 3)
        if item is not None:
            return item.text()
        else:
            return None

    def rafraichir_nb_lignes_tableau(self):
        totalfile=self.table_widget.rowCount()
        self.label_totalfichiers.setText(f"{totalfile}")
        return

    def supprimer_premiere_ligne(self):
        if self.table_widget.rowCount() > 0:
            self.table_widget.removeRow(0)

    def analyze_directory(self, dir_name):
        file_info_list = []
        totalfile = 0
        for root, dirs, files in os.walk(dir_name):
            for file in files:
                full_path = os.path.join(root, file)
                file_path = os.path.dirname(full_path)
                # En Mo
                file_size_megabytes = os.path.getsize(full_path)/ (1024 * 1024)
                file_size=f"{file_size_megabytes:.2f} Mo"
                # creation
                #creation_time = QDateTime.fromSecsSinceEpoch(int(os.path.getctime(full_path))).toString()
                # Modification
                creation_time = QDateTime.fromSecsSinceEpoch(int(os.path.getmtime(full_path))).toString()
                
                file_info_list.append((file,file_size,creation_time,file_path))
                # Nb fichiers
                totalfile = totalfile + 1

        # Set table dimensions
        self.table_widget.setRowCount(len(file_info_list))
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Name", "Size","Modification Time","Path"])

        # Populate table with file information
        for row, (file_name,file_size,creation_time,file_path) in enumerate(file_info_list):
            self.table_widget.setItem(row, 0, QTableWidgetItem(file_name))
            self.table_widget.setItem(row, 1, QTableWidgetItem(file_size))
            self.table_widget.setItem(row, 2, QTableWidgetItem(creation_time))
            self.table_widget.setItem(row, 3, QTableWidgetItem(file_path))

        # Affichage du nombre de fichiers
        self.label_totalfichiers.setText(f"{totalfile}")

        # Adjust column widths to fit content
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def display_image(self, row, column):
        file_path = self.table_widget.item(row, 3).text()
        file_name = self.table_widget.item(row, 0).text()
        file_full_path=file_path+"/"+file_name

        if os.path.isfile(file_full_path) and file_full_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            pixmap = QPixmap(file_full_path)

            # Get screen size
            screen_size = QApplication.primaryScreen().size()
            screen_width = screen_size.width()
            screen_height = screen_size.height()

            # Scale pixmap to fit screen size while keeping aspect ratio
            scaled_pixmap = pixmap.scaled(int(screen_width * 0.8), int(screen_height * 0.8),Qt.AspectRatioMode.KeepAspectRatio)
            scaled_pixmap_preview = pixmap.scaled(900, 600, Qt.AspectRatioMode.KeepAspectRatio)
            # Display the image in the right layout
            self.image_label.setPixmap(scaled_pixmap_preview)


            # msg_box = QMessageBox()
            # msg_box.setIconPixmap(scaled_pixmap)
            # msg_box.setWindowTitle("Image Preview - "+file_name)
            # msg_box.setStandardButtons(QMessageBox.StandardButton.Cancel)
            # msg_box.addButton(QMessageBox.StandardButton.Ok)
            # delete_button = msg_box.addButton("Supprimer", QMessageBox.ButtonRole.ActionRole)

            # def handle_delete():
            #     print("Suppression")
            #     os.remove(file_path)  # Delete the file
            #     msg_box.done(0)  # Close the message box
            #     # Refresh the table data
            #     dir_name = os.path.dirname(file_path)
            #     self.analyze_directory(dir_name)

            #delete_button.clicked.connect(handle_delete)

            # def handle_key_press(event):
            #     if event.key() == Qt.Key.Key_A:
            #         confirm_msg = QMessageBox()
            #         confirm_msg.setIcon(QMessageBox.Icon.Warning)
            #         confirm_msg.setText(f"Voulez-vous vraiment supprimer le fichier {file_path} ?")
            #         confirm_msg.setWindowTitle("Confirmer la suppression")
            #         confirm_msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            #         ret = confirm_msg.exec()

            #         if ret == QMessageBox.StandardButton.Yes:
            #             print(f"Fichier {file_path} supprimé.")
            #             os.remove(file_path)  # Delete the file
            #             msg_box.done(0)  # Close the message box
            #             # Refresh the table data
            #             dir_name = os.path.dirname(file_path)
            #             self.analyze_directory(dir_name)

            # msg_box.keyPressEvent = handle_key_press

            # msg_box.exec()

    def show_message(self,titre,message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle(titre)
        msg_box.exec()

    def quit_application(self):
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
