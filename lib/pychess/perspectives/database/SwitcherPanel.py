# -*- coding: UTF-8 -*-
from __future__ import print_function

import os

from gi.repository import Gtk, GObject
from gi.repository.GdkPixbuf import Pixbuf

from pychess.Utils.IconLoader import load_icon

pgn_icon = load_icon(32, "application-x-chess-pgn", "pychess")
CLIPBASE = "Clipbase"


class SwitcherPanel(Gtk.IconView):
    __gsignals__ = {
        'chessfile_switched': (GObject.SignalFlags.RUN_FIRST, None, (object, )),
    }

    def __init__(self, persp):
        GObject.GObject.__init__(self)
        self.persp = persp

        self.persp.connect("chessfile_opened", self.on_chessfile_opened)
        self.persp.connect("chessfile_closed", self.on_chessfile_closed)
        self.persp.connect("chessfile_imported", self.on_chessfile_imported)

        self.alignment = Gtk.Alignment()

        self.liststore = Gtk.ListStore(object, Pixbuf, str, str)
        self.set_model(self.liststore)
        self.set_pixbuf_column(1)
        self.set_text_column(2)
        self.set_tooltip_column(3)
        self.set_item_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_activate_on_single_click(True)
        self.set_selection_mode(Gtk.SelectionMode.BROWSE)

        self.connect("item-activated", self.on_item_activated)

        self.alignment.add(self)
        self.alignment.show_all()

        treepath = Gtk.TreePath(0)
        self.select_path(treepath)

    def on_item_activated(self, iconview, path):
        treeiter = self.liststore.get_iter(path)
        chessfile = self.liststore.get_value(treeiter, 0)
        self.emit("chessfile_switched", chessfile)

    def on_chessfile_opened(self, persp, chessfile):
        name, ext = os.path.splitext(chessfile.path)
        icon = pgn_icon
        basename = os.path.basename(name)
        info = "%s\n%s  %s" % (basename, ext[1:], chessfile.count)
        tooltip = chessfile.path
        treeiter = self.liststore.append([chessfile, icon, info, tooltip])
        treepath = self.liststore.get_path(treeiter)
        self.select_path(treepath)

    def on_chessfile_closed(self, persp):
        for i, row in enumerate(self.liststore):
            if row[0] == self.persp.chessfile:
                # print("removing %s" % self.persp.chessfile.path)
                # first remove the closed
                treeiter = self.liststore.get_iter(Gtk.TreePath(i))
                self.liststore.remove(treeiter)

                # then select the previous
                if i > 0:
                    treepath = Gtk.TreePath(i - 1)
                    self.select_path(treepath)
                    self.item_activated(treepath)
                else:
                    if len(self.liststore) > 0:
                        treepath = Gtk.TreePath(0)
                        self.select_path(treepath)
                        self.item_activated(treepath)
                self.queue_draw()
                break

    def on_chessfile_imported(self, persp, chessfile):
        name, ext = os.path.splitext(chessfile.path)
        # basename = os.path.basename(name)
        info = "%s\n%s  %s" % (name, ext[1:], chessfile.count)

        for i, row in enumerate(self.liststore):
            if row[0] == self.persp.chessfile:
                treeiter = self.liststore.get_iter(Gtk.TreePath(i))
                self.liststore[treeiter][2] = info
                break
