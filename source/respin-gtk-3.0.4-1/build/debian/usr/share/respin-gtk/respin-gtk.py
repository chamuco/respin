#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#Licence: GPLv3.0
#Copyright: Krasimir S. Stefanov <lokiisyourmaster@gmail.com>
#Modified by: Marcia Wilbur <aicra@faqlinux.com>

try:
    import sys
    import os
    import os.path
    import stat
    import locale
    import gettext
    import pygtk
    pygtk.require("2.0")
    import gtk
    import gtk.glade
    import re
    import shutil
    import datetime
    import time
    import subprocess
    import shlex
    import ConfigParser
    import vte
except:
    print "Please install all dependencies!"
    sys.exit(1)

APP = "respin"
DIR = "/usr/share/locale"
APP_VERSION = "3.0.4-1"

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext

LOCALE = locale.getlocale()[0]

class appgui:
    def __init__(self):
        self.pathname = os.path.dirname(sys.argv[0])
        self.abspath = os.path.abspath(self.pathname)
        self.gladefile = self.abspath + "/respin-gtk.glade"
        self.window1 = gtk.glade.XML(self.gladefile,"window1",APP)
        self.working_dir = os.path.expanduser("~")
        self.callback_id = 0
        
        dic = {
            "on_button1_clicked" : self.on_button1_clicked,
            "on_button2_clicked" : self.on_button2_clicked,
            "on_button3_clicked" : self.on_button3_clicked,
            "on_button4_clicked" : self.on_button4_clicked,
            "on_button5_clicked" : self.on_button5_clicked,
            "on_button6_clicked" : self.on_button6_clicked,
            "on_button7_clicked" : self.quit,
            "on_button8_clicked" : self.on_button8_clicked,
            "on_button9_clicked" : self.on_button9_clicked,
            "on_button10_clicked" : self.on_button10_clicked,
            "on_button11_clicked" : self.on_button11_clicked,
            "on_button12_clicked" : self.on_button12_clicked,
            "on_button13_clicked" : self.on_button13_clicked,
            "on_window1_delete_event" : self.quit
        }
        
        self.window1.signal_autoconnect (dic)
        self.v = vte.Terminal ()
        self.window1.get_widget("vbox2").add(self.v)
        self.v.show()
        self.load_settings()
        msg_info(_("It is necessary to close all other linux and unmount any network shares while running Respin Backup. Please do so now and then click OK when you are ready to continue."), self.window1.get_widget("window1"))
        
    def run_command(self, cmd, done_callback):
        argv = shlex.split(cmd)
        self.callback_id = self.v.connect ("child-exited", done_callback)
        self.v.fork_command(argv[0], argv)
        #self.v.feed_child('set -e\n')
        self.window1.get_widget("notebook1").set_current_page(2)
        self.v.show()
        #self.v.feed_child(cmd+'\nexit 0\n')

    def on_button1_clicked(self,widget):
        self.update_conf()
        if not msg_confirm(_("You have selected Backup Mode. Do not interrupt this process. Click OK to Start the Backup LiveCD/DVD process."), self.window1.get_widget("window1")):
            return
        self.run_command('respin backup', self.on_backup_done)

    def on_backup_done(self, widget, data = None):
        if self.v.get_child_exit_status() == 0:
            WORKDIR = self.window1.get_widget("entry6").get_text()
            CUSTOMISO = self.window1.get_widget("entry3").get_text()
            msg_info(_("Your %(iso)s and %(iso)s.md5 files are ready in %(dir)s. It is recommended to test it in a virtual machine or on a rewritable cd/dvd to ensure it works as desired. Click on OK to return to the main menu.") 
                % ({"iso" : CUSTOMISO, "dir" : WORKDIR+'/respin'}), self.window1.get_widget("window1"))
        else:
            msg_error(_("The process was interrupted!"), self.window1.get_widget("window1"))
        self.window1.get_widget("notebook1").set_current_page(0)
        self.v.handler_disconnect(self.callback_id)

    def on_button2_clicked(self,widget):
        self.update_conf()
        if not msg_confirm(_("You have selected Dist Mode. Click OK to Start the Distributable LiveCD/DVD process."), self.window1.get_widget("window1")):
            return
        self.run_command('respin dist', self.on_dist_done)

    def on_dist_done(self, widget, data = None):
        
        if self.v.get_child_exit_status() == 0:
            WORKDIR = self.window1.get_widget("entry6").get_text()
            CUSTOMISO = self.window1.get_widget("entry3").get_text()
            msg_info(_("Your %(iso)s and %(iso)s.md5 files are ready in %(dir)s. It is recommended to test it in a virtual machine or on a rewritable cd/dvd to ensure it works as desired. Click on OK to return to the main menu.") % ({"iso" : CUSTOMISO, "dir" : WORKDIR+'/respin'}))
        else:
            msg_error(_("The process was interrupted!"), self.window1.get_widget("window1"))
        self.window1.get_widget("notebook1").set_current_page(0)
        self.v.handler_disconnect(self.callback_id)
        
    def on_button3_clicked(self,widget):
        self.update_conf()
        if not msg_confirm(_("You have selected Dist CDFS Mode. Click OK to Start the Distributable LiveCD/DVD filesystem build process.")):
            return
        self.run_command('respin dist cdfs', self.on_dist_cdfs_done)

    def on_dist_cdfs_done(self, widget, data = None):
        if self.v.get_child_exit_status() == 0:
            WORKDIR = self.window1.get_widget("entry6").get_text()
            CUSTOMISO = self.window1.get_widget("entry3").get_text()
            msg_info(_("Your livecd filesystem is ready in %s. You can now add files to the cd and then run the Distiso option when you are done. Click on OK to return to the main menu.") % WORKDIR+'/respin')
        else:
            msg_error(_("The process was interrupted!"), self.window1.get_widget("window1"))
        self.window1.get_widget("notebook1").set_current_page(0)
        self.v.handler_disconnect(self.callback_id)
    
    def on_button4_clicked(self,widget):
        self.update_conf()
        WORKDIR = self.window1.get_widget("entry6").get_text()
        if os.path.exists(WORKDIR+'/respin/ISOTMP/casper/filesystem.squashfs'):
            if not msg_confirm(_("You have selected Dist ISO Mode. Click OK to create the iso file.")):
                self.window1.get_widget("window1").show()
                return
            self.run_command('respin dist iso', self.on_dist_iso_done)
        else:
            msg_error(_("The livecd filesystem does not exist. Click OK to go back to the main menu and try the normal Dist mode or the Dist CDFS again."))

    def on_dist_iso_done(self, widget, data = None):
        if self.v.get_child_exit_status() == 0:
            WORKDIR = self.window1.get_widget("entry6").get_text()
            CUSTOMISO = self.window1.get_widget("entry3").get_text()
            msg_info(_("Your %(iso)s and %(iso)s.md5 files are ready in %(dir)s. It is recommended to test it in a virtual machine or on a rewritable cd/dvd to ensure it works as desired. Click on OK to return to the main menu.") % ({"iso" : CUSTOMISO, "dir" : WORKDIR+'/respin'}))
        else:
            msg_error(_("The process was interrupted!"), self.window1.get_widget("window1"))
        self.window1.get_widget("notebook1").set_current_page(0)
        self.v.handler_disconnect(self.callback_id)
        
    def on_button5_clicked(self,widget):
        self.update_conf()
        if not msg_confirm(_("This will remove all the files from the temporary directory. Click OK to proceed.")):
            return
        #os.system('respin clean')
        self.run_command('respin clean', self.on_clean_done)
        #msg_info(_("Completed. Click OK to return to the main menu."))

    def on_clean_done(self, widget, data = None):
        if self.v.get_child_exit_status() == 0:
            msg_info(_("Completed. Click OK to return to the main menu."))
        else:
            msg_error(_("The process was interrupted!"), self.window1.get_widget("window1"))
        self.window1.get_widget("notebook1").set_current_page(0)
        self.v.handler_disconnect(self.callback_id)
        
    def on_button6_clicked(self,widget):
        # show about dialog
        about = gtk.AboutDialog()
        about.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        about.set_program_name(_("Respin"))
        about.set_version(APP_VERSION)
        about.set_authors([_("Krasimir S. Stefanov <lokiisyourmaster@gmail.com>"),_("Marcia Wilbur <aicra@faqlinux.com>")])
        about.set_website("http://www.linuxrespin.com/")
        translators = [
            _("Bulgarian - Krasimir S. Stefanov <lokiisyourmaster@gmail.com>"),
            _("English - Krasimir S. Stefanov <lokiisyourmaster@gmail.com>"), _("Traditional Chinese - Kent Chang <kentxchang@gmail.com>")
        ]

        about.set_translator_credits('\n'.join(translators))
        about.set_logo_icon_name('respin-gtk')
        license = _('''PyGTK GUI for Respin
Copyright (C) 2011 Krasimir S. Stefanov, Tony Brijeski
Licence: GPLv3.0
http://www.gnu.org/licenses/.''')
        about.set_license(license)
        about.run()
        about.hide()

    def on_button8_clicked(self,widget):
        dialog = gtk.FileChooserDialog(_("Select working directory"),
            None,
            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
            
        dialog.set_default_response(gtk.RESPONSE_OK)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.window1.get_widget("entry6").set_text(dialog.get_filename())
        dialog.destroy()

    def on_button9_clicked(self,widget):
        dialog = gtk.FileChooserDialog(title=_("Select 640x480 PNG image..."),action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_current_folder(self.working_dir)
        
        filter = gtk.FileFilter()
        filter.set_name(_("PNG Images"))
        filter.add_mime_type("image/png")
        dialog.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name(_("All files"))
        filter.add_pattern("*")
        dialog.add_filter(filter)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            now = datetime.datetime.now()
            filename = dialog.get_filename()
            dialog.destroy()  
            self.working_dir = os.path.dirname(filename)
            shutil.move("/etc/respin/isolinux/splash.png", "/etc/respin/isolinux/splash.png." + now.strftime("%Y%m%d%H%M%S"))
            shutil.copy(filename, "/etc/respin/isolinux/splash.png")
            msg_info(_("%s has been copied to /etc/respin/isolinux/splash.png becoming the default background for the LIVE menu.") % filename)
        else:
            dialog.destroy()                  

    def on_button10_clicked(self,widget):
        dialog = gtk.FileChooserDialog(title=_("Select image..."),action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_current_folder(self.working_dir)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            now = datetime.datetime.now()
            filename = dialog.get_filename()
            self.working_dir = os.path.dirname(filename)
            name, ext = os.path.splitext(filename)
            grub_bg = "/etc/respin/grub" + ext
            shutil.copy(filename, grub_bg)
            dialog.destroy()
            
            
            grub = open('/etc/default/grub').read()
            
            m = re.search('(#?)GRUB_BACKGROUND=.*', grub)
            if m != None:
                grub.replace(m.group(0), 'GRUB_BACKGROUND="%s"' % grub_bg)
            else:
                grub += '\nGRUB_BACKGROUND="%s"' % grub_bg
            
            f = open('/etc/default/grub', 'w+')
            f.write(grub)
            f.close()
            
            msg_info(_("%(filename)s has been copied to %(grub_bg)s and is the default background for grub. Click OK to update grub with the new settings so you can see your picture on the next boot.") % ({'filename':filename, 'grub_bg':grub_bg}))
            self.window1.get_widget("label17").hide()
            self.window1.get_widget("progressbar1").show()
            process = subprocess.Popen(['update-grub'], stdout=subprocess.PIPE, stderr=None)
            while process.poll() == None:
                while gtk.events_pending():
                    gtk.main_iteration_do()
                time.sleep(.1) 
                self.window1.get_widget("progressbar1").pulse()
            process.wait()
            self.window1.get_widget("progressbar1").hide()
            self.window1.get_widget("label17").show()
            msg_info(_("GRUB has been updated."))
        else:
            dialog.destroy()        

    
    def on_button11_clicked(self,widget):
        self.window1.get_widget("window1").hide()
        def cancel(widget, other = None):
            ns.window.get_widget("window2").destroy()
            self.window1.get_widget("window1").show()
        
        def ok(widget, other = None):
            model, treeiter = ns.window.get_widget("treeview1").get_selection().get_selected()
            username = model.get(treeiter, 0)[0]
            ns.window.get_widget("progressbar1").show()
            ns.window.get_widget("hbuttonbox1").set_sensitive(False)
            process = subprocess.Popen(['respin-skelcopy', username], stdout=subprocess.PIPE, stderr=None)
            while process.poll() == None:
                while gtk.events_pending():
                    gtk.main_iteration_do()
                time.sleep(.1) 
                ns.window.get_widget("progressbar1").pulse()
            process.wait()
            ns.window.get_widget("progressbar1").hide()
            ns.window.get_widget("hbuttonbox1").set_sensitive(True)
            ns.window.get_widget("window2").destroy()
            self.window1.get_widget("window1").show()
            
        
        ns = Namespace()
        ns.window = gtk.glade.XML(self.gladefile,"window2" ,APP)
        gtk.glade.bindtextdomain(APP,DIR)
        dic = {
            "on_window2_delete_event" : (cancel)
            , "on_button1_clicked" :  (cancel)
            , "on_button2_clicked" :  (ok)
        }
        ns.window.signal_autoconnect (dic)


        ns.liststore = gtk.ListStore(str, str)
        ns.window.get_widget("treeview1").set_model(ns.liststore)
        ns.tvcolumn1 = gtk.TreeViewColumn(_('User'))        
        ns.tvcolumn2 = gtk.TreeViewColumn(_('Home directory'))        
        
        ns.cell1 = gtk.CellRendererText()
        ns.cell2 = gtk.CellRendererText()

        ns.tvcolumn1.pack_start(ns.cell1, True)
        ns.tvcolumn2.pack_start(ns.cell2, True)
        ns.tvcolumn1.set_attributes(ns.cell1, text=0)
        ns.tvcolumn2.set_attributes(ns.cell2, text=1)

        ns.window.get_widget("treeview1").append_column(ns.tvcolumn1)
        ns.window.get_widget("treeview1").append_column(ns.tvcolumn2)
        

        passwd = open('/etc/passwd', 'r').read().strip().split('\n')
        for row in passwd:
            data = row.split(':')
            if int(data[2]) >= 1000 and int(data[2]) <= 1100:
                ns.liststore.append([data[0], data[5]])
        ns.window.get_widget("window2").show()
               
    def on_button12_clicked(self,widget):
        self.window1.get_widget("window1").hide()

        def auto(widget, other = None):
            active = ns.window.get_widget("checkbutton1").get_active()
            ns.window.get_widget("treeview1").set_sensitive(not active)
            
        def update_initramfs():
            ns.window.get_widget("progressbar1").show()
            ns.window.get_widget("hbuttonbox1").set_sensitive(False)
            uname = os.popen('uname -r').read().strip()
            process = subprocess.Popen(['mkinitramfs', '-o', '/boot/initrd.img-'+uname, uname], stdout=subprocess.PIPE, stderr=None)
            while process.poll() == None:
                while gtk.events_pending():
                    gtk.main_iteration_do()
                time.sleep(.1) 
                ns.window.get_widget("progressbar1").pulse()
            process.wait()
            ns.window.get_widget("progressbar1").hide()
            ns.window.get_widget("hbuttonbox1").set_sensitive(True)
        
        def cancel(widget, other = None):
            ns.window.get_widget("window3").destroy()
            self.window1.get_widget("window1").show()
        
        def ok(widget, other = None):
            if ns.window.get_widget("checkbutton1").get_active():
                os.system("update-alternatives --auto default.plymouth")
                update_initramfs()
                msg_info(_("Done! Now plymouth will use the default, auto-selected theme."))
            else:
                model, treeiter = ns.window.get_widget("treeview1").get_selection().get_selected()
                if treeiter == None:
                    msg_error(_("Please, select a theme!"))
                    return
                theme = model.get(treeiter, 1)[0]
                os.system('update-alternatives --set default.plymouth "%s"' % theme)
                update_initramfs()
            ns.window.get_widget("window3").destroy()
            self.window1.get_widget("window1").show()
            
        def create(widget, other = None):
            theme_name = msg_input('', _('Enter your plymouth theme name. eg. Respin Theme (please use only alphanumeric characters)'), _('Name:'), 'Respin Theme')          
            if theme_name == False or theme_name == None:
                return
            elif theme_name == '':
                msg_error(_("You must specify theme name!"))
                return
            
            theme_name_fixed = theme_name.replace(' ','-').replace('/','-').replace('..','-').replace('\\','-')
            theme_dir = "/lib/plymouth/themes/" + theme_name_fixed
            
            if os.path.exists(theme_dir):
                overwrite = msg_confirm(_('The theme "%s" already exists! Do you want to overwrite it?') % theme_name)
                if overwrite:
                    shutil.rmtree(theme_dir)
                else:
                    return
            
            dialog = gtk.FileChooserDialog(title=_("Select 1920x1080 PNG image..."),action=gtk.FILE_CHOOSER_ACTION_OPEN,
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            dialog.set_default_response(gtk.RESPONSE_OK)
            dialog.set_current_folder(self.working_dir)
            
            filter = gtk.FileFilter()
            filter.set_name(_("PNG Images"))
            filter.add_mime_type("image/png")
            dialog.add_filter(filter)

            filter = gtk.FileFilter()
            filter.set_name(_("All files"))
            filter.add_pattern("*")
            dialog.add_filter(filter)
            
            response = dialog.run()
            if response == gtk.RESPONSE_OK:
                filename = dialog.get_filename()
                self.working_dir = os.path.dirname(filename)
                dialog.destroy()
                while gtk.events_pending():
                    gtk.main_iteration_do()
                os.makedirs(theme_dir)
                now = datetime.datetime.now()
                theme_pic = os.path.join(theme_dir, os.path.basename(filename))
                shutil.copy(filename, theme_pic)
                shutil.copy('/etc/respin/plymouth/respin-theme/progress_bar.png', theme_dir+'/progress_bar.png')
                shutil.copy('/etc/respin/plymouth/respin-theme/progress_box.png', theme_dir+'/progress_box.png')
                script_name = "/lib/plymouth/themes/"+theme_name_fixed+"/"+theme_name_fixed+".script"
                script = open("/etc/respin/plymouth/respin-theme/respin-theme.script").read().replace("__THEMEPIC__", os.path.basename(theme_pic))
                open(script_name, 'w+').write(script)
                
                config_name = "/lib/plymouth/themes/"+theme_name_fixed+"/"+theme_name_fixed+".plymouth"
                config = open("/etc/respin/plymouth/respin-theme/respin-theme.plymouth").read()
                config = config.replace("__THEMENAME__", theme_name)
                config = config.replace("__THEMEDIR__", theme_name_fixed)
                open(config_name, 'w+').write(config)
                
                
                os.system('update-alternatives --install /lib/plymouth/themes/default.plymouth default.plymouth "%(config_name)s" 80' % ({'config_name': config_name}))
                os.system('update-alternatives --set default.plymouth "%(config_name)s"' % ({'config_name': config_name}))
                
                ns.window.get_widget("checkbutton1").set_active(False)
                
                update_initramfs()
                
                msg_info(_("Your plymouth theme named %(theme_name)s with the picture %(theme_pic)s has been created.") % ({'theme_name': theme_name, 'theme_pic': theme_pic}))
            else:
                dialog.destroy()
                shutil.rmtree(theme_dir)
            list_themes()
            
        def preview(widget, other = None):
            if not os.path.isfile('/lib/plymouth/renderers/x11.so'):
                msg_error(_("In order to be able to preview plymouth themes, you have to install plymouth-x11!"))
                return
                
            output = os.popen('update-alternatives --display default.plymouth').read().strip()
            m = re.search('default.plymouth - (manual|auto) mode', output)
            if m == None:
                ns.window.get_widget("window3").show()
                return
            mode = m.group(1)
            
            if mode == 'auto':
                ns.window.get_widget("window3").hide()
                while gtk.events_pending():
                    gtk.main_iteration_do()
                os.system("plymouth-preview")
                ns.window.get_widget("window3").show()
            else:
                model, treeiter = ns.window.get_widget("treeview1").get_selection().get_selected()
                if treeiter == None:
                    msg_error(_("Please, select a theme!"))
                    return
                theme = model.get(treeiter, 1)[0]
                ns.window.get_widget("window3").hide()
                while gtk.events_pending():
                    gtk.main_iteration_do()
                    
                    
                output = os.popen('update-alternatives --display default.plymouth').read().strip()
                m = re.search('default.plymouth - (manual|auto) mode', output)
                if m == None:
                    ns.window.get_widget("window3").show()
                    return
                mode = m.group(1)
                
                m = re.search('link\s*currently\s*points\s*to\s*(.*)', output)
                if m == None:
                    ns.window.get_widget("window3").show()
                    return
                link = m.group(1)

                os.system('update-alternatives --set default.plymouth "%s"' % theme)
                os.system("plymouth-preview")
                ns.window.get_widget("window3").show()
                
                if mode == 'auto':
                    os.system('update-alternatives --auto default.plymouth')
                else:
                    os.system('update-alternatives --set default.plymouth "%s"' % link)
        
        def list_themes():
            ns.liststore.clear()
            output = os.popen('update-alternatives --display default.plymouth').read().strip()
            m = re.search('default.plymouth - (manual|auto) mode', output)
            if m == None:
                ns.window.get_widget("window3").show()
                return
            mode = m.group(1)
            m = re.search('link\s*currently\s*points\s*to\s*(.*)', output)
            if m == None:
                ns.window.get_widget("window3").show()
                return
            link = m.group(1)
            lines = os.popen('update-alternatives --list default.plymouth').read().strip().split('\n')
            for row in lines:
                if row != "":
                    config = ConfigParser.ConfigParser()
                    config.readfp(open(row))
                    name = config.get('Plymouth Theme', 'Name')
                    iter = ns.liststore.append([name, row])
                    if mode == 'manual' and row == link:
                        ns.window.get_widget("treeview1").get_selection().select_iter(iter)
            ns.window.get_widget("checkbutton1").set_active(mode == 'auto')
            
        ns = Namespace()
        ns.window = gtk.glade.XML(self.gladefile,"window3" ,APP)
        gtk.glade.bindtextdomain(APP,DIR)
        dic = {
            "on_window3_delete_event" : (cancel)
            , "on_button1_clicked" :  (cancel)
            , "on_button2_clicked" :  (ok)
            , "on_button3_clicked" :  (create)
            , "on_button4_clicked" :  (preview)
            , "on_checkbutton1_toggled" :  (auto)
        }
        ns.window.signal_autoconnect (dic)


        ns.liststore = gtk.ListStore(str, str)
        ns.window.get_widget("treeview1").set_model(ns.liststore)
        ns.tvcolumn1 = gtk.TreeViewColumn(_('Name'))        
        ns.tvcolumn2 = gtk.TreeViewColumn(_('Directory'))        
        
        ns.cell1 = gtk.CellRendererText()
        ns.cell2 = gtk.CellRendererText()

        ns.tvcolumn1.pack_start(ns.cell1, True)
        ns.tvcolumn2.pack_start(ns.cell2, True)
        ns.tvcolumn1.set_attributes(ns.cell1, text=0)
        ns.tvcolumn2.set_attributes(ns.cell2, text=1)

        ns.window.get_widget("treeview1").append_column(ns.tvcolumn1)
        ns.window.get_widget("treeview1").append_column(ns.tvcolumn2)
        list_themes()
        ns.window.get_widget("window3").show()
        

    def on_button13_clicked(self,widget):
        if msg_confirm(_("Are you sure you want to delete the contents of /etc/skel?")):
            shutil.rmtree('/etc/skel/')
            os.makedirs('/etc/skel/')
       
    def quit(self, widget, data = None):
        self.update_conf()
        gtk.main_quit()
        exit(0)
        
    def load_settings(self):
        config_f = open("/etc/respin.conf")
        config_txt = config_f.read()
        config_f.close()
        
        self.window1.get_widget("entry1").set_text(
            self.getvalue('LIVEUSER', config_txt, 'custom'))

        self.window1.get_widget("entry2").set_text(
            self.getvalue('LIVECDLABEL', config_txt, 'Custom Live CD'))

        self.window1.get_widget("entry3").set_text(
            self.getvalue('CUSTOMISO', config_txt, 'custom-$1.iso'))

        self.window1.get_widget("entry4").set_text(
            self.getvalue('EXCLUDES', config_txt, ''))
    
        self.window1.get_widget("entry5").set_text(
            self.getvalue('LIVECDURL', config_txt, 'http://www.respin.com'))

        self.window1.get_widget("entry7").set_text(
            self.getvalue('SQUASHFSOPTS', config_txt, '-no-recovery -always-use-fragments -b 1M -no-duplicates'))

        self.window1.get_widget("checkbutton1").set_active(
            self.getvalue('BACKUPSHOWINSTALL', config_txt, '1') == '1')
        
        workdir = self.getvalue('WORKDIR', config_txt, '/home/respin')
        if not os.path.exists(workdir):
            os.makedirs(workdir)
        self.window1.get_widget("entry6").set_text(workdir)
        
        self.window1.get_widget("checkbutton1").set_active(
            self.getvalue('BACKUPSHOWINSTALL', config_txt, '1').upper() == '1')

    def update_conf(self):
        if self.window1.get_widget("checkbutton1").get_active():
            BACKUPSHOWINSTALL = '1'
        else:
            BACKUPSHOWINSTALL = '0'
            
        conf_content = '''
#Respin Global Configuration File


# This is the temporary working directory and won't be included on the cd/dvd
WORKDIR="%(WORKDIR)s"


# Here you can add any other files or directories to be excluded from the live filesystem
# Separate each entry with a space
EXCLUDES="%(EXCLUDES)s"


# Here you can change the livecd/dvd username
LIVEUSER="%(LIVEUSER)s"


# Here you can change the name of the livecd/dvd label
LIVECDLABEL="%(LIVECDLABEL)s"


# Here you can change the name of the ISO file that is created
CUSTOMISO="%(CUSTOMISO)s"

# Here you can change the mksquashfs options
SQUASHFSOPTS="%(SQUASHFSOPTS)s"


# Here you can prevent the Install icon from showing up on the desktop in backup mode. 0 - to not show 1 - to show 
BACKUPSHOWINSTALL="%(BACKUPSHOWINSTALL)s"


# Here you can change the url for the usb-creator info
LIVECDURL="%(LIVECDURL)s"
''' % ({
        "WORKDIR" : self.window1.get_widget("entry6").get_text(),
        "EXCLUDES" : self.window1.get_widget("entry4").get_text(),
        "LIVEUSER" : self.window1.get_widget("entry1").get_text(),
        "LIVECDLABEL" : self.window1.get_widget("entry2").get_text(),
        "CUSTOMISO" : self.window1.get_widget("entry3").get_text(),
        "SQUASHFSOPTS" : self.window1.get_widget("entry7").get_text(),
        "BACKUPSHOWINSTALL" : BACKUPSHOWINSTALL,
        "LIVECDURL" : self.window1.get_widget("entry5").get_text()
        })
        
        conf = open('/etc/respin.conf', 'w+')
        conf.write(conf_content)
        conf.close()
        
    def getvalue(self, name, conf, default):
        try:
            m = re.search(name+'="(.*)"',conf)
            return m.group(1)
        except:
            return default


def msg_error(msg, window = None):
    dialog = gtk.MessageDialog(
        window,
        gtk.DIALOG_MODAL,
        gtk.MESSAGE_ERROR,
        gtk.BUTTONS_OK, msg
    )
    dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
    dialog.run()
    dialog.destroy()
            
def msg_info(msg, window = None):
    dialog = gtk.MessageDialog(
        window,
        gtk.DIALOG_MODAL,
        gtk.MESSAGE_INFO,
        gtk.BUTTONS_OK,
        msg
    )
    dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
    dialog.run()
    dialog.destroy()        

def msg_confirm(msg, window = None):
    dialog = gtk.MessageDialog(
        window
        , gtk.DIALOG_DESTROY_WITH_PARENT
        , gtk.MESSAGE_QUESTION
        , gtk.BUTTONS_OK_CANCEL
        , msg
    )
    dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
    response = dialog.run()
    dialog.destroy()

    if response == gtk.RESPONSE_OK:
        return True
    else:
        return False

def msg_input(title, message, label, default = '', window = None, password = False):
    def responseToDialog( entry, dialog, response):
        dialog.response(response)

    dialog = gtk.MessageDialog(
        window,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_QUESTION,
        gtk.BUTTONS_OK_CANCEL,
        None
    )
    dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
    dialog.set_markup(message)
    dialog.set_title(title)

    entry = gtk.Entry()
    entry.set_text(default)
    entry.set_visibility(not password)
    entry.connect("activate", responseToDialog, dialog, gtk.RESPONSE_OK)
    hbox = gtk.HBox()
    hbox.pack_start(gtk.Label(label), False, 5, 5)
    hbox.pack_end(entry)
    dialog.vbox.pack_end(hbox, True, True, 0)
    dialog.show_all()
    response = dialog.run()
    text = entry.get_text()
    dialog.destroy()
    
    if response == gtk.RESPONSE_OK:
        return text
    else:
        return None

class Namespace: pass

if os.popen('whoami').read().strip() != 'root':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    if os.system('which gksu')==0:
        if os.path.exists('/usr/share/applications/respin-gtk.desktop'):
            os.system('gksu -D "%s" ./respin-gtk.py' % _('Respin'))
        else:
            os.system('gksu -D "%s" ./respin-gtk.py' % '/usr/share/applications/respin-gtk.desktop')
    elif os.system('which kdesudo')==0:
        os.system('kdesudo ./respin-gtk.py' )
    elif os.system('which sudo')==0:
        password = msg_input(_(''), _('Enter your password to perform administrative tasks'), 'Password:', '', None, True)
        if password:
            os.popen('sudo -S ./respin-gtk.py','w').write(password)
else:
    if __name__ == '__main__':
        app = appgui()
        gtk.main()

