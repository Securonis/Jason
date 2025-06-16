#!/usr/bin/env python3
# Jason - Privacy and Security Tool
# Author:root0emir

import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QHBoxLayout, QMessageBox)
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QProcess

class JasonGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tor_enabled = False
        self.autostart_enabled = False
        self.ramwipe_enabled = False
        self.wipe_enabled = False
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Jason - Privacy Tool')
        self.setMinimumSize(600, 500)
        
        # Set up the main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Create a cream background
        cream_palette = QPalette()
        cream_palette.setColor(QPalette.Window, QColor(255, 253, 240))
        cream_palette.setColor(QPalette.WindowText, QColor(30, 30, 30))
        self.setPalette(cream_palette)
        
        # Title and description
        title_label = QLabel('JASON')
        title_label.setFont(QFont('Arial', 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        desc_label = QLabel('Privacy and Security Tool')
        desc_label.setFont(QFont('Arial', 12))
        desc_label.setAlignment(Qt.AlignCenter)
        
        # Add title and description to the layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(desc_label)
        main_layout.addSpacing(20)
        
        # Create buttons with dark theme
        self.tor_button = self.create_dark_button("Start Tor Routing")
        self.autostart_button = self.create_dark_button("Enable Autostart")
        self.autowipe_button = self.create_dark_button("Enable Auto Wipe")
        self.restart_tor_button = self.create_dark_button("Restart Tor")
        self.ip_check_button = self.create_dark_button("Check IP")
        self.about_button = self.create_dark_button("About")
        self.exit_button = self.create_dark_button("Exit")
        
        # Add buttons to layout
        main_layout.addWidget(self.tor_button)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.autostart_button)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.autowipe_button)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.restart_tor_button)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.ip_check_button)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.about_button)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.exit_button)
        main_layout.addStretch()
        
        # Set up button connections
        self.tor_button.clicked.connect(self.toggle_tor)
        self.autostart_button.clicked.connect(self.toggle_autostart)
        self.autowipe_button.clicked.connect(self.toggle_autowipe)
        self.restart_tor_button.clicked.connect(self.restart_tor)
        self.ip_check_button.clicked.connect(self.check_ip)
        self.about_button.clicked.connect(self.show_about)
        self.exit_button.clicked.connect(self.close)
        
        # Set the central widget
        self.setCentralWidget(main_widget)
        
        # Check the current status of services
        self.check_service_status()
    
    def create_dark_button(self, text):
        """Create a dark themed button with hover effects"""
        button = QPushButton(text)
        button.setMinimumHeight(50)
        button.setFont(QFont('Arial', 12))
        
        # Dark theme styling
        button.setStyleSheet("""
            QPushButton {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #3D3D3D;
            }
            QPushButton:pressed {
                background-color: #1D1D1D;
            }
        """)
        
        return button
    
    def check_service_status(self):
        """Check the current status of Jason services"""
        # Check Tor status
        try:
            # First check if jason-tor.service is enabled/active
            result = subprocess.run(['systemctl', 'is-active', '--quiet', 'jason-tor'], 
                                   check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.tor_enabled = (result.returncode == 0)
            
            # If not enabled via systemd, check if tor is running
            if not self.tor_enabled:
                result = subprocess.run(['systemctl', 'is-active', '--quiet', 'tor'], 
                                      check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.tor_enabled = (result.returncode == 0)
            
            # Check if Jason's iptables rules are active (simplified check)
            try:
                result = subprocess.run(['grep', '-q', 'jason', '/etc/network/iptables.rules'],
                                      check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode == 0:
                    self.tor_enabled = True
            except:
                pass
                
            # Update Tor button text
            if self.tor_enabled:
                self.tor_button.setText("Stop Tor Routing")
            else:
                self.tor_button.setText("Start Tor Routing")
                
        except Exception as e:
            print(f"Error checking Tor status: {e}")
        
        # Check Autostart status (jason-tor service enabled at boot)
        try:
            result = subprocess.run(['systemctl', 'is-enabled', '--quiet', 'jason-tor'],
                                   check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.autostart_enabled = (result.returncode == 0)
            
            # Update Autostart button text
            if self.autostart_enabled:
                self.autostart_button.setText("Disable Autostart")
            else:
                self.autostart_button.setText("Enable Autostart")
                
        except Exception as e:
            print(f"Error checking Autostart status: {e}")
        
        # Check Autowipe status (jason-autowipe service)
        try:
            result = subprocess.run(['systemctl', 'is-enabled', '--quiet', 'jason-autowipe'],
                                   check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.autowipe_enabled = (result.returncode == 0)
            
            # Update Autowipe button text
            if self.autowipe_enabled:
                self.autowipe_button.setText("Disable Auto Wipe")
            else:
                self.autowipe_button.setText("Enable Auto Wipe")
                
        except Exception as e:
            print(f"Error checking Autowipe status: {e}")
    
    def toggle_tor(self):
        """Toggle Tor routing service"""
        if self.tor_enabled:
            # Disable Tor
            try:
                subprocess.run(['sudo', '/usr/bin/jason', 'stop'], 
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.tor_enabled = False
                self.tor_button.setText("Start Tor Routing")
                QMessageBox.information(self, "Jason", "Tor routing disabled successfully.")
            except subprocess.CalledProcessError:
                QMessageBox.critical(self, "Error", "Failed to disable Tor routing. Check logs for details.")
        else:
            # Enable Tor
            try:
                subprocess.run(['sudo', '/usr/bin/jason', 'start'], 
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.tor_enabled = True
                self.tor_button.setText("Stop Tor Routing")
                QMessageBox.information(self, "Jason", "Tor routing enabled successfully.")
            except subprocess.CalledProcessError:
                QMessageBox.critical(self, "Error", "Failed to enable Tor routing. Check logs for details.")
    
    def toggle_autowipe(self):
        """Toggle Auto Wipe service"""
        if self.autowipe_enabled:
            # Disable Autowipe
            try:
                subprocess.run(['sudo', 'systemctl', 'stop', 'jason-autowipe'], 
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                subprocess.run(['sudo', 'systemctl', 'disable', 'jason-autowipe'], 
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.autowipe_enabled = False
                self.autowipe_button.setText("Enable Auto Wipe")
                QMessageBox.information(self, "Jason", "Auto Wipe disabled successfully.")
            except subprocess.CalledProcessError:
                QMessageBox.critical(self, "Error", "Failed to disable Auto Wipe. Check logs for details.")
        else:
            # Enable Autowipe
            try:
                subprocess.run(['sudo', 'systemctl', 'enable', 'jason-autowipe'], 
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                subprocess.run(['sudo', 'systemctl', 'start', 'jason-autowipe'], 
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.autowipe_enabled = True
                self.autowipe_button.setText("Disable Auto Wipe")
                QMessageBox.information(self, "Jason", "Auto Wipe enabled successfully.")
            except subprocess.CalledProcessError:
                QMessageBox.critical(self, "Error", "Failed to enable Auto Wipe. Check logs for details.")
            
    def toggle_autostart(self):
        """Toggle Autostart for Jason"""
        if self.autostart_enabled:
            # Disable Autostart
            try:
                # Remove from systemd boot
                subprocess.run(['sudo', 'systemctl', 'disable', 'jason-tor'], 
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.autostart_enabled = False
                self.autostart_button.setText("Enable Autostart")
                QMessageBox.information(self, "Jason", "Autostart disabled successfully.")
            except subprocess.CalledProcessError:
                QMessageBox.critical(self, "Error", "Failed to disable Autostart. Check logs for details.")
        else:
            # Enable Autostart
            try:
                # Add to systemd boot
                subprocess.run(['sudo', 'systemctl', 'enable', 'jason-tor'], 
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.autostart_enabled = True
                self.autostart_button.setText("Disable Autostart")
                QMessageBox.information(self, "Jason", "Autostart enabled successfully.")
            except subprocess.CalledProcessError:
                QMessageBox.critical(self, "Error", "Failed to enable Autostart. Check logs for details.")
                
    def toggle_wipe(self):
        """Toggle Wipe service"""
        if self.wipe_enabled:
            # Disable Wipe
            try:
                subprocess.run(['sudo', 'systemctl', 'stop', 'jason-wipe'], 
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                subprocess.run(['sudo', 'systemctl', 'disable', 'jason-wipe'], 
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.wipe_enabled = False
                self.update_button_text(self.wipe_button, "Jason Wipe", False)
                QMessageBox.information(self, "Jason", "Wipe disabled successfully.")
            except subprocess.CalledProcessError:
                QMessageBox.critical(self, "Error", "Failed to disable Wipe. Check logs for details.")
        else:
            # Enable Wipe
            try:
                subprocess.run(['sudo', 'systemctl', 'enable', 'jason-wipe'], 
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                subprocess.run(['sudo', 'systemctl', 'start', 'jason-wipe'], 
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.wipe_enabled = True
                self.update_button_text(self.wipe_button, "Jason Wipe", True)
                QMessageBox.information(self, "Jason", "Wipe enabled successfully.")
            except subprocess.CalledProcessError:
                QMessageBox.critical(self, "Error", "Failed to enable Wipe. Check logs for details.")
    

    def change_tor_id(self):
        """Change the Tor identity by triggering the jason change command"""
        try:
            subprocess.run(['sudo', '/usr/bin/jason', 'change'], 
                          check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            QMessageBox.information(self, "Jason", "Tor identity changed successfully.")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Failed to change Tor identity: {str(e)}")
    
    def restart_tor(self):
        """Restart Tor service using the jason restart command"""
        try:
            result = QMessageBox.warning(self, "Jason", 
                                        "Are you sure you want to restart Tor?", 
                                        QMessageBox.Yes | QMessageBox.No)
            
            if result == QMessageBox.Yes:
                # Show a "please wait" message
                self.statusBar().showMessage("Restarting Tor, please wait...")
                QApplication.processEvents()
                
                # Run the restart command
                subprocess.run(['sudo', '/usr/bin/jason', 'restart'], 
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                self.statusBar().clearMessage()
                QMessageBox.information(self, "Jason", "Tor service restarted successfully.")
                
                # Update button status
                self.check_service_status()
        except subprocess.CalledProcessError as e:
            self.statusBar().clearMessage()
            QMessageBox.critical(self, "Error", f"Failed to restart Tor: {str(e)}")
    
    def check_ip(self):
        """Check the current IP address using the jason myip command"""
        try:
            # Show warning about potential risk
            result = QMessageBox.warning(self, "Jason - Security Warning", 
                                       "Checking your IP address may expose your system to fingerprinting risks.\n\n" 
                                       "This is considered RISKY and only recommended if absolutely necessary.\n\n"
                                       "Do you want to continue?", 
                                       QMessageBox.Yes | QMessageBox.No)
            
            if result == QMessageBox.Yes:
                # Show a "please wait" message
                self.statusBar().showMessage("Checking IP, please wait...")
                QApplication.processEvents()
                
                # Run the IP check command
                process = subprocess.run(['sudo', '/usr/bin/jason', 'myip'], 
                                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       universal_newlines=True)
                
                # Extract the IP information from the output
                output = process.stdout
                
                self.statusBar().clearMessage()
                # Create a custom dialog to show the IP information
                ip_dialog = QDialog(self)
                ip_dialog.setWindowTitle("Your Current IP")
                ip_dialog.setMinimumWidth(400)
                ip_dialog.setMinimumHeight(300)
                
                layout = QVBoxLayout(ip_dialog)
                
                # Create a text browser to show the output with formatting preserved
                text_browser = QTextBrowser()
                text_browser.setText(output)
                layout.addWidget(text_browser)
                
                # Add a close button
                close_button = QPushButton("Close")
                close_button.clicked.connect(ip_dialog.close)
                layout.addWidget(close_button)
                
                ip_dialog.exec_()
                
        except subprocess.CalledProcessError as e:
            self.statusBar().clearMessage()
            QMessageBox.critical(self, "Error", f"Failed to check IP address: {str(e)}")
    
    def show_about(self):
        """Show information about Jason"""
        about_text = """<b>Jason Privacy Tool</b><br><br>
        Jason is a comprehensive privacy and security tool designed to protect your digital fingerprint.<br>
        <br>
        <b>Features:</b><br>
        • Route all traffic through Tor for anonymity<br>
        • Change Tor identity as needed<br>
        • Autowipe memory to protect sensitive data<br>
        • Full system wipe on shutdown<br>
        <br>
        This tool helps you stay private in an increasingly surveilled world.<br>
        <br>
        <b>Version:</b> 1.0<br>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About Jason")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(about_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for a more modern look
    window = JasonGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    # Check if running as root, if not, relaunch with sudo
    if os.geteuid() != 0:
        args = ['sudo', sys.executable] + sys.argv
        os.execlp('sudo', *args)
    else:
        main()
