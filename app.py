from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import struct
import threading

app = Flask(__name__)

DATA_FILE = "data.json"
plc_locks = {}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"process_name": "", "plcs": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_plc_lock(plc_id):
    if plc_id not in plc_locks:
        plc_locks[plc_id] = threading.Lock()
    return plc_locks[plc_id]

def connect_plc(plc_cfg):
    try:
        import snap7
        client = snap7.client.Client()
        client.connect(plc_cfg["ip_address"], int(plc_cfg["rack"]), int(plc_cfg["slot"]))
        return client, None
    except ImportError:
        return None, "snap7 not installed"
    except Exception as e:
        return None, str(e)

def read_value(client, var_cfg):
    area_map = {
        "DB": 0x84, "M": 0x83, "I": 0x81, "Q": 0x82,
        "T": 0x1D, "C": 0x1C
    }
    data_type = var_cfg["data_type"]
    area = var_cfg["memory_area"]
    db_num = int(var_cfg.get("db_number", 0) or 0)
    start = int(var_cfg["start_byte"])
    bit = int(var_cfg.get("bit_number", 0) or 0)

    try:
        import snap7
        from snap7.util import get_bool, get_int, get_real, get_dint, get_word, get_dword, get_byte

        if data_type == "BOOL":
            data = client.read_area(area_map[area], db_num, start, 1)
            return bool(get_bool(data, 0, bit))
        elif data_type == "BYTE":
            data = client.read_area(area_map[area], db_num, start, 1)
            return get_byte(data, 0)
        elif data_type == "INT":
            data = client.read_area(area_map[area], db_num, start, 2)
            return get_int(data, 0)
        elif data_type == "DINT":
            data = client.read_area(area_map[area], db_num, start, 4)
            return get_dint(data, 0)
        elif data_type == "WORD":
            data = client.read_area(area_map[area], db_num, start, 2)
            return get_word(data, 0)
        elif data_type == "DWORD":
            data = client.read_area(area_map[area], db_num, start, 4)
            return get_dword(data, 0)
        elif data_type == "REAL":
            data = client.read_area(area_map[area], db_num, start, 4)
            return get_real(data, 0)
        else:
            return None
    except Exception as e:
        raise e

def write_value(client, var_cfg, value):
    area_map = {
        "DB": 0x84, "M": 0x83, "I": 0x81, "Q": 0x82,
        "T": 0x1D, "C": 0x1C
    }
    data_type = var_cfg["data_type"]
    area = var_cfg["memory_area"]
    db_num = int(var_cfg.get("db_number", 0) or 0)
    start = int(var_cfg["start_byte"])
    bit = int(var_cfg.get("bit_number", 0) or 0)

    try:
        import snap7
        from snap7.util import set_bool, set_int, set_real, set_dint, set_word, set_dword, set_byte
        import bytearray as ba

        if data_type == "BOOL":
            data = client.read_area(area_map[area], db_num, start, 1)
            set_bool(data, 0, bit, bool(int(value)))
            client.write_area(area_map[area], db_num, start, data)
        elif data_type == "BYTE":
            data = bytearray(1)
            set_byte(data, 0, int(value))
            client.write_area(area_map[area], db_num, start, data)
        elif data_type == "INT":
            data = bytearray(2)
            set_int(data, 0, int(value))
            client.write_area(area_map[area], db_num, start, data)
        elif data_type == "DINT":
            data = bytearray(4)
            set_dint(data, 0, int(value))
            client.write_area(area_map[area], db_num, start, data)
        elif data_type == "WORD":
            data = bytearray(2)
            set_word(data, 0, int(value))
            client.write_area(area_map[area], db_num, start, data)
        elif data_type == "DWORD":
            data = bytearray(4)
            set_dword(data, 0, int(value))
            client.write_area(area_map[area], db_num, start, data)
        elif data_type == "REAL":
            data = bytearray(4)
            set_real(data, 0, float(value))
            client.write_area(area_map[area], db_num, start, data)
    except Exception as e:
        raise e

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    data = load_data()
    if not data.get("process_name"):
        return render_template("setup.html", data=data)
    return redirect(url_for("page_one"))

@app.route("/setup", methods=["POST"])
def setup():
    data = load_data()
    data["process_name"] = request.form.get("process_name", "").strip()
    save_data(data)
    return redirect(url_for("page_one"))

@app.route("/config")
def page_one():
    data = load_data()
    if not data.get("process_name"):
        return redirect(url_for("index"))
    return render_template("page_one.html", data=data)

@app.route("/monitor")
def page_two():
    data = load_data()
    if not data.get("process_name"):
        return redirect(url_for("index"))
    return render_template("page_two.html", data=data)

@app.route("/api/process_name", methods=["POST"])
def update_process_name():
    data = load_data()
    body = request.get_json()
    data["process_name"] = body.get("name", "").strip()
    save_data(data)
    return jsonify({"ok": True, "name": data["process_name"]})

@app.route("/api/plc", methods=["POST"])
def add_plc():
    data = load_data()
    body = request.get_json()
    plc = {
        "id": str(len(data["plcs"]) + 1) + "_" + body["name"].replace(" ", "_"),
        "name": body["name"],
        "ip_address": body["ip_address"],
        "rack": body["rack"],
        "slot": body["slot"],
        "variables": []
    }
    data["plcs"].append(plc)
    save_data(data)
    return jsonify({"ok": True, "plc": plc})

@app.route("/api/plc/<plc_id>", methods=["DELETE"])
def delete_plc(plc_id):
    data = load_data()
    data["plcs"] = [p for p in data["plcs"] if p["id"] != plc_id]
    save_data(data)
    return jsonify({"ok": True})

@app.route("/api/plc/<plc_id>/variable", methods=["POST"])
def add_variable(plc_id):
    data = load_data()
    body = request.get_json()
    for plc in data["plcs"]:
        if plc["id"] == plc_id:
            var = {
                "id": str(len(plc["variables"]) + 1) + "_" + body["name"].replace(" ", "_"),
                "name": body["name"],
                "memory_area": body["memory_area"],
                "db_number": body.get("db_number", ""),
                "data_type": body["data_type"],
                "start_byte": body["start_byte"],
                "bit_number": body.get("bit_number", ""),
            }
            plc["variables"].append(var)
            save_data(data)
            return jsonify({"ok": True, "variable": var})
    return jsonify({"ok": False, "error": "PLC not found"}), 404

@app.route("/api/plc/<plc_id>/variable/<var_id>", methods=["DELETE"])
def delete_variable(plc_id, var_id):
    data = load_data()
    for plc in data["plcs"]:
        if plc["id"] == plc_id:
            plc["variables"] = [v for v in plc["variables"] if v["id"] != var_id]
            save_data(data)
            return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "PLC not found"}), 404

@app.route("/api/plc/<plc_id>/read", methods=["GET"])
def read_plc(plc_id):
    data = load_data()
    plc_cfg = next((p for p in data["plcs"] if p["id"] == plc_id), None)
    if not plc_cfg:
        return jsonify({"ok": False, "error": "PLC not found"}), 404

    lock = get_plc_lock(plc_id)
    with lock:
        client, err = connect_plc(plc_cfg)
        if err:
            return jsonify({"ok": False, "error": err, "values": {}})

        results = {}
        errors = {}
        try:
            for var in plc_cfg["variables"]:
                try:
                    val = read_value(client, var)
                    results[var["id"]] = val
                except Exception as e:
                    errors[var["id"]] = str(e)
        finally:
            try:
                client.disconnect()
            except:
                pass

    return jsonify({"ok": True, "values": results, "errors": errors})

@app.route("/api/plc/<plc_id>/write/<var_id>", methods=["POST"])
def write_plc(plc_id, var_id):
    data = load_data()
    plc_cfg = next((p for p in data["plcs"] if p["id"] == plc_id), None)
    if not plc_cfg:
        return jsonify({"ok": False, "error": "PLC not found"}), 404

    var_cfg = next((v for v in plc_cfg["variables"] if v["id"] == var_id), None)
    if not var_cfg:
        return jsonify({"ok": False, "error": "Variable not found"}), 404

    body = request.get_json()
    value = body.get("value")

    lock = get_plc_lock(plc_id)
    with lock:
        client, err = connect_plc(plc_cfg)
        if err:
            return jsonify({"ok": False, "error": err})
        try:
            write_value(client, var_cfg, value)
            new_val = read_value(client, var_cfg)
            return jsonify({"ok": True, "value": new_val})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)})
        finally:
            try:
                client.disconnect()
            except:
                pass

@app.route("/api/plc/<plc_id>/test", methods=["GET"])
def test_plc(plc_id):
    data = load_data()
    plc_cfg = next((p for p in data["plcs"] if p["id"] == plc_id), None)
    if not plc_cfg:
        return jsonify({"ok": False, "error": "PLC not found"}), 404
    client, err = connect_plc(plc_cfg)
    if err:
        return jsonify({"ok": False, "error": err})
    try:
        info = client.get_cpu_info()
        client.disconnect()
        return jsonify({"ok": True, "info": str(info)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
