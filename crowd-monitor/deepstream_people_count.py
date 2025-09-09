#!/usr/bin/env python3
import sys, gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import pyds
import math
Gst.init(None)
def intersect(A, B, C, D):
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

# Track center points of each person
track_history = {}
crossed_ids = {}

IN_COUNT = 0
OUT_COUNT = 0
# Define line coordinates (replace with your actual config_nvdsanalytics.txt line values)
OUT_LINE = [(737, 328), (1018, 328)]
IN_LINE = [(740, 300), (1012, 296)]

# --- Put this at top of your file (if not already) ---
# Some pyds builds don't expose analytics meta constants; we'll detect by cast instead.
# NVDSANALYTICS_FRAME_META = 100  # optional fallback, not used below

def osd_sink_pad_buffer_probe(pad, info, u_data):
    global IN_COUNT, OUT_COUNT, crossed_ids, track_history

    try:
        buf = info.get_buffer()
        if not buf:
            return Gst.PadProbeReturn.OK

        batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(buf))
        if not batch_meta:
            return Gst.PadProbeReturn.OK

        l_frame = batch_meta.frame_meta_list
        while l_frame:
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
            if not frame_meta:
                l_frame = l_frame.next
                continue

            # ---- 1) IN/OUT counting ----
            obj_meta_list = frame_meta.obj_meta_list
            while obj_meta_list:
                obj_meta = pyds.NvDsObjectMeta.cast(obj_meta_list.data)
                if obj_meta and obj_meta.class_id == 0 and obj_meta.object_id != 0xFFFFFFFF:
                    tracking_id = obj_meta.object_id
                    x_center = int(obj_meta.rect_params.left + obj_meta.rect_params.width / 2)
                    y_center = int(obj_meta.rect_params.top + obj_meta.rect_params.height / 2)
                    current_point = (x_center, y_center)

                    if tracking_id not in track_history:
                        track_history[tracking_id] = []
                    track_history[tracking_id].append(current_point)
                    if len(track_history[tracking_id]) > 30:
                        track_history[tracking_id].pop(0)

                    if tracking_id not in crossed_ids:
                        crossed_ids[tracking_id] = set()

                    if len(track_history[tracking_id]) >= 2 and not crossed_ids[tracking_id]:
                        prev_point = track_history[tracking_id][-2]
                        if intersect(IN_LINE[0], IN_LINE[1], prev_point, current_point):
                            IN_COUNT += 1
                            crossed_ids[tracking_id].add("IN")
                        elif intersect(OUT_LINE[0], OUT_LINE[1], prev_point, current_point):
                            OUT_COUNT += 1
                            crossed_ids[tracking_id].add("OUT")

                obj_meta_list = obj_meta_list.next

            # ---- 2) Prepare display text ----
            #display_text = f"IN: {IN_COUNT}  |  OUT: {OUT_COUNT}"

            # ---- 3) Overcrowding detection (robust) ----
            # Instead of relying on missing constants, try casting user_meta.user_meta_data
            user_meta_list = frame_meta.frame_user_meta_list
            found_analytics = False
            while user_meta_list is not None:
                try:
                    user_meta = pyds.NvDsUserMeta.cast(user_meta_list.data)
                    if not user_meta:
                        user_meta_list = user_meta_list.next
                        continue

                    # Try to cast the user_meta.user_meta_data to NvDsAnalyticsFrameMeta
                    try:
                        analytics_meta = pyds.NvDsAnalyticsFrameMeta.cast(user_meta.user_meta_data)
                        # If cast succeeded and has ocStatus attribute, use it
                        if analytics_meta and getattr(analytics_meta, "ocStatus", None) is not None:
                            found_analytics = True
                            # ocStatus is typically a dict mapping roi_name -> bool
                            for roi_name, status in analytics_meta.ocStatus.items():
                                if status:
                                    # add one alert line per frame if any ROI overcrowded
                                    display_text += "\nCrowd Detected!"
                                    print(f"[ALERT] Overcrowding detected in {roi_name}")
                    except Exception:
                        # Not analytics user meta; skip silently
                        pass

                except Exception as e:
                    # Defensive: log and continue
                    print("Warning: failed to cast user_meta:", e)

                user_meta_list = user_meta_list.next

            if not found_analytics:
                # debug hint: uncomment for more info once to confirm analytics is running
                # print("No analytics user-meta found in this frame.")
                pass

            # ---- 4) Acquire and populate display meta ----
            try:
                display_meta = pyds.nvds_acquire_display_meta_from_pool(batch_meta)
                display_meta = pyds.nvds_acquire_display_meta_from_pool(batch_meta)
                display_meta.num_labels = 2  # two separate text labels

                # ---- ALERT line (top) ----
                alert_text_params = display_meta.text_params[0]
                alert_text_params.display_text = "⚠ ALERT: Overcrowd Detected"
                alert_text_params.x_offset = 50
                alert_text_params.y_offset = 30   # top position
                alert_text_params.font_params.font_name = "Serif"
                alert_text_params.font_params.font_size = 28
                alert_text_params.font_params.font_color.set(1.0, 0.0, 0.0, 1.0)  # red
                alert_text_params.set_bg_clr = 1
                alert_text_params.text_bg_clr.set(0.0, 0.0, 0.0, 1)  # semi-transparent black

                # ---- IN/OUT counts (below) ----
                #count_text_params = display_meta.text_params[1]
                #count_text_params.display_text = f"IN: {IN_COUNT}  |  OUT: {OUT_COUNT}"
                #count_text_params.x_offset = 50
                #count_text_params.y_offset = 70   # below alert line
                #count_text_params.font_params.font_name = "Serif"
                #count_text_params.font_params.font_size = 20
                #count_text_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)  # white
                #count_text_params.set_bg_clr = 1
                #count_text_params.text_bg_clr.set(0.0, 0.0, 0.0, 0.6)

                pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)

                if display_meta:
                    # set num_labels equal to newline-count +1 so OSD allocates enough lines
                    display_meta.num_labels = display_text.count("\n") + 1

                    display_meta.text_params[0].display_text = display_text
                    display_meta.text_params[0].x_offset = 50
                    display_meta.text_params[0].y_offset = 50
                    display_meta.text_params[0].font_params.font_name = "Serif"
                    display_meta.text_params[0].font_params.font_size = 20
                    font_color = pyds.NvOSD_ColorParams()
                    font_color.red = 1.0; font_color.green = 1.0; font_color.blue = 1.0; font_color.alpha = 1.0
                    display_meta.text_params[0].font_params.font_color = font_color
                    display_meta.text_params[0].set_bg_clr = 1
                    bg_color = pyds.NvOSD_ColorParams()
                    bg_color.red = 0.0; bg_color.green = 0.0; bg_color.blue = 0.0; bg_color.alpha = 0.6
                    display_meta.text_params[0].text_bg_clr = bg_color

                    # draw lines
                    line1 = pyds.NvOSD_LineParams()
                    line1.x1, line1.y1 = IN_LINE[0]; line1.x2, line1.y2 = IN_LINE[1]
                    blue = pyds.NvOSD_ColorParams(); blue.red=0.0; blue.green=0.0; blue.blue=1.0; blue.alpha=1.0
                    line1.line_color = blue; line1.line_width = 4

                    line2 = pyds.NvOSD_LineParams()
                    line2.x1, line2.y1 = OUT_LINE[0]; line2.x2, line2.y2 = OUT_LINE[1]
                    red = pyds.NvOSD_ColorParams(); red.red=1.0; red.green=0.0; red.blue=0.0; red.alpha=1.0
                    line2.line_color = red; line2.line_width = 4

                    display_meta.num_lines = 2
                    display_meta.line_params[0] = line1
                    display_meta.line_params[1] = line2

                    pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)
                else:
                    print("Warning: could not acquire display_meta")
            except Exception as e:
                print("Error creating/pushing display_meta:", e)

            l_frame = l_frame.next

    except Exception as e:
        import traceback
        print("Unhandled exception in osd_sink_pad_buffer_probe:", e)
        traceback.print_exc()

    return Gst.PadProbeReturn.OK




def bus_call(bus, msg, loop):
    t = msg.type
    if t == Gst.MessageType.EOS:
        print("EOS reached"); loop.quit()
    elif t == Gst.MessageType.ERROR:
        err, dbg = msg.parse_error()
        print(f"ERROR: {err}, {dbg}"); loop.quit()
    return True

def main():
    pipeline = Gst.Pipeline.new()
    src = Gst.ElementFactory.make("filesrc", "src")
    src.set_property("location", "sam2.mp4")
    dec = Gst.ElementFactory.make("decodebin", "dec")
    mux = Gst.ElementFactory.make("nvstreammux", "mux")
    mux.set_property("width", 1920); mux.set_property("height", 1080)
    mux.set_property("batch-size", 1); mux.set_property("batched-push-timeout", 40000)
    pgie = Gst.ElementFactory.make("nvinfer", "pgie")
    pgie.set_property("config-file-path", "config_infer_primary_yolo11.txt")
    tracker = Gst.ElementFactory.make("nvtracker", "tracker")
    tracker.set_property("tracker-width", 640); tracker.set_property("tracker-height", 384)
    tracker.set_property("gpu-id", 0)
    tracker.set_property("ll-lib-file", "/opt/nvidia/deepstream/deepstream-7.1/lib/libnvds_nvmultiobjecttracker.so")
    tracker.set_property("ll-config-file", "config_tracker_NvDCF_perf.yml")
    analytics = Gst.ElementFactory.make("nvdsanalytics", "analytics")
    analytics.set_property("config-file", "config_nvdsanalytics.txt")
    conv = Gst.ElementFactory.make("nvvideoconvert", "conv")
    osd = Gst.ElementFactory.make("nvdsosd", "osd")
    sink = Gst.ElementFactory.make("nveglglessink", "sink")

    for e in [src, dec, mux, pgie, tracker, analytics, conv, osd, sink]:
        if not e: print("Error creating element", e); sys.exit(1)

    pipeline.add(src); pipeline.add(dec); pipeline.add(mux)
    pipeline.add(pgie); pipeline.add(tracker); pipeline.add(analytics)
    pipeline.add(conv); pipeline.add(osd); pipeline.add(sink)

    src.link(dec)
    def on_pad(_, pad):
        cap = pad.get_current_caps().to_string()
        if cap.startswith("video"):
            pad.link(mux.get_request_pad("sink_0"))
    dec.connect("pad-added", on_pad)

    mux.link(pgie); pgie.link(tracker); tracker.link(analytics)
    analytics.link(conv); conv.link(osd); osd.link(sink)
 
    osd.get_static_pad("sink").add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, None)

    pipeline.set_state(Gst.State.PLAYING)
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)
    loop.run()
    pipeline.set_state(Gst.State.NULL)

if __name__ == "__main__":
    main()
