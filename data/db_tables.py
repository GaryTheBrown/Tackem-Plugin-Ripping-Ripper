'''Database Tables'''
from libs.sql.column import Column

AUDIO_CONVERT_DB_INFO = {
    "name": "ripping_ripper_audio_convert_info",
    "data":
        [
            Column("id", "integer", primary_key=True, not_null=True),
            Column("info_id", "integer", not_null=True),
            Column("filename", "text", not_null=True),
            Column("track_info", "json"),
            Column("converted", "bit", not_null=True, default=False),
        ],
    "version": 1
}

AUDIO_INFO_DB_INFO = {
    "name": "ripping_ripper_audio_info",
    "data":
        [
            Column("id", "integer", primary_key=True, not_null=True),
            Column("musicbrainz_disc_id", "varchar(28)", not_null=True),
            Column("track_count", "tinyint", not_null=True),
            Column("release_id", "varchar(36)", not_null=True),
            Column("disc_data", "json"),
            Column("ripped", "bit", not_null=True, default=False),
            Column("ready_to_convert", "bit", not_null=True, default=False),
            Column("ready_to_rename", "bit", not_null=True, default=False),
            Column("ready_for_library", "bit", not_null=True, default=False),
            Column("completed", "bit", not_null=True, default=False),
        ],
    "version": 1
}


VIDEO_CONVERT_DB_INFO = {
    "name": "ripping_ripper_video_convert_info",
    "data":
        [
            Column("id", "integer", primary_key=True, not_null=True),
            Column("info_id", "integer", not_null=True),
            Column("filename", "text", not_null=True),
            Column("disc_info", "json"),
            Column("track_data", "json"),
            Column("converted", "bit", not_null=True, default=False),
        ],
    "version": 1
}

VIDEO_INFO_DB_INFO = {
    "name": "ripping_ripper_video_info",
    "data":
        [
            Column("id", "integer", primary_key=True, not_null=True),
            Column("uuid", "varchar(16)", not_null=True),
            Column("label", "text", not_null=True),
            Column("sha256", "varchar(64)", not_null=True),
            Column("disc_type", "varchar(6)", not_null=True),
            Column("rip_data", "json"),
            Column("ripped", "bit", not_null=True, default=False),
            Column("ready_to_convert", "bit", not_null=True, default=False),
            Column("ready_to_rename", "bit", not_null=True, default=False),
            Column("ready_for_library", "bit", not_null=True, default=False),
            Column("completed", "bit", not_null=True, default=False),
        ],
    "version": 1
}
