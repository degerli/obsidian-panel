__author__ = "Nigshoxiz"

from flask import render_template, abort, request, redirect, send_file
import os, json, shutil, traceback

from app import db, app
from app.controller.global_config import GlobalConfig
from app.utils import returnModel, generate_random_string, KVParser
from app.model import JavaBinary, ServerCORE, ServerInstance, FTPAccount, Users

from . import server_inst_page, logger, version
from app.blueprints.superadmin.check_login import check_login, ajax_check_login

rtn = returnModel("string")

@server_inst_page.route("/edit_inst/<inst_id>", methods=["GET"])
@check_login
def render_edit_index_page(uid, priv, inst_id):
    return render_template("/server_inst/index.html", new_inst_page=0, version = version)

@server_inst_page.route("/edit_inst/<inst_id>/init_edit_data", methods=["GET"])
@ajax_check_login
def get_init_edit_data(uid, priv, inst_id):
    _model = {
        # general
        "number_players" : None,
        "world_name" : "",
        "number_RAM" : None,
        "listen_port" : None,

        # core & java version
        "server_cores_list" : [],
        "java_versions_list" : [],

        "core_file_id" : None,
        "java_bin_id" : None,
        # server properties
        "server_properties" : {},

        # LOGO & MOTD
        # Notice: MOTD is contained in server_properties
        # as for LOGO, there's another API fetching its info

        # FTP account
        "ftp_account_name" : None,
        "default_ftp_password" : None
    }

    try:
        # 1. check if it's authorizable to get data from inst_id
        _q = db.session.query(ServerInstance).filter(ServerInstance.inst_id == int(inst_id)).filter(ServerInstance.owner_id == uid).first()

        if _q == None:
            return rtn.error(403)
        # 2. get general info from ServerInstance table
        _model["number_players"] = _q.max_user
        _model["number_RAM"] = _q.max_RAM / 1024
        _model["world_name"] = _q.inst_name
        _model["listen_port"] = _q.listening_port

        _model["core_file_id"] = _q.core_file_id
        _model["java_bin_id"] = _q.java_bin_id

        # 3. get core file list & java version list
        java_versions_obj = db.session.query(JavaBinary).all()
        java_versions = _model["java_versions_list"]
        for item in java_versions_obj:
            __model = {
                "name" : "1.%s.0_%s" % (item.major_version, item.minor_version),
                "index" : item.id,
            }

            java_versions.append(__model)

        server_cores = _model["server_cores_list"]
        server_cores_obj = db.session.query(ServerCORE).all()
        for item in server_cores_obj:
            if item.core_version != None and item.core_version != "":
                _name = "%s-%s-%s" % (item.core_type, item.core_version, item.minecraft_version)
            else:
                _name = "%s-%s" % (item.core_type, item.minecraft_version)
            __model = {
                "name" : _name,
                "index" : item.core_id
            }

            server_cores.append(__model)

        # 4. read server properties
        file_server_properties = os.path.join(_q.inst_dir,"server.properties")
        if os.path.exists(file_server_properties):
            parser = KVParser(file_server_properties)
            _model["server_properties"] = parser.conf_items

        # 5. read FTP info
        ftp_obj = db.session.query(FTPAccount).filter(FTPAccount.inst_id == inst_id).first()
        if ftp_obj != None:
            _model["ftp_account_name"] = ftp_obj.username
            _model["default_ftp_password"] = ftp_obj.default_password

        return rtn.success(_model)
    except:
        logger.error(traceback.format_exc())
        return rtn.error(500)
