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

    # Per-frame display text (always start defined)
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

            # --- initialize display_text for this frame ---
            display_text = f"IN: {IN_COUNT}  |  OUT: {OUT_COUNT}"
            crowd_alerted = False

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

            # ---- 2) Overcrowding detection (robust) ----
            # Choose a safe default threshold (overrideable)
            FRAME_OVERCROWD_THRESHOLD = 50  # change this to what you consider "crowd"
            user_meta_list = frame_meta.frame_user_meta_list
            found_analytics = False
            while user_meta_list is not None:
                try:
                    user_meta = pyds.NvDsUserMeta.cast(user_meta_list.data)
                    if not user_meta:
                        user_meta_list = user_meta_list.next
                        continue

                    # Try to cast to analytics frame meta
                    try:
                        analytics_meta = pyds.NvDsAnalyticsFrameMeta.cast(user_meta.user_meta_data)
                        if analytics_meta:
                            found_analytics = True
                            # Defensive: print structure once if you are debugging
                            # print("DEBUG analytics_meta fields:", dir(analytics_meta))
                            # print("DEBUG ocStatus:", getattr(analytics_meta, "ocStatus", None))

                            oc_status = getattr(analytics_meta, "ocStatus", None)
                            if oc_status:
                                # oc_status may be dict-like mapping roi_name -> <bool|int|...>
                                for roi_name, status in oc_status.items():
                                    # If status is boolean use it directly
                                    if isinstance(status, bool):
                                        if status:
                                            crowd_alerted = True
                                            display_text += "\nCrowd Detected!"
                                            print(f"[ALERT] Overcrowding boolean in {roi_name}")
                                    # If status is numeric treat it as count (compare to threshold)
                                    elif isinstance(status, (int, float)):
                                        # Prefer a threshold from analytics_meta if it exists
                                        threshold = getattr(analytics_meta, "ocThreshold", FRAME_OVERCROWD_THRESHOLD)
                                        if status >= threshold:
                                            crowd_alerted = True
                                            display_text += f"\nCrowd Detected in {roi_name} (count={status})"
                                            print(f"[ALERT] Overcrowding in {roi_name}: {status} >= {threshold}")
                                    else:
                                        # Fallback: treat non-empty/truthy values as alert only if > 1 kind of indicator
                                        if status:
                                            crowd_alerted = True
                                            display_text += f"\nCrowd Detected (roi:{roi_name})"
                                            print(f"[ALERT] Overcrowding (unknown type) in {roi_name}: {status}")
                    except Exception:
                        # not analytics user meta
                        pass

                except Exception as e:
                    print("Warning: failed to cast user_meta:", e)

                user_meta_list = user_meta_list.next

            # ---- 3) Acquire and populate display meta once ----
            try:
                display_meta = pyds.nvds_acquire_display_meta_from_pool(batch_meta)
                if not display_meta:
                    print("Warning: could not acquire display_meta")
                else:
                    # ensure at least 1 label
                    display_meta.num_labels = display_text.count("\n") + 1
                    # use text_params[0] to display combined info
                    tp = display_meta.text_params[0]
                    tp.display_text = display_text
                    tp.x_offset = 50
                    tp.y_offset = 50
                    tp.font_params.font_name = "Serif"
                    tp.font_params.font_size = 27
                    tp.set_bg_clr = 1
                    tp.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)
                    tp.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)

                    # draw lines (one-time per frame)
                    display_meta.num_lines = 2
                    line1 = pyds.NvOSD_LineParams()
                    line1.x1, line1.y1 = IN_LINE[0]; line1.x2, line1.y2 = IN_LINE[1]
                    line1.line_width = 4
                    blue = pyds.NvOSD_ColorParams(); blue.red=0.0; blue.green=0.0; blue.blue=1.0; blue.alpha=1.0
                    line1.line_color = blue

                    line2 = pyds.NvOSD_LineParams()
                    line2.x1, line2.y1 = OUT_LINE[0]; line2.x2, line2.y2 = OUT_LINE[1]
                    line2.line_width = 4
                    red = pyds.NvOSD_ColorParams(); red.red=1.0; red.green=0.0; red.blue=0.0; red.alpha=1.0
                    line2.line_color = red

                    display_meta.line_params[0] = line1
                    display_meta.line_params[1] = line2

                    pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)

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
    src.set_property("location", "sam2.mp4") # Your Video 
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
