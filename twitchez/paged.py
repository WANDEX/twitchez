#!/usr/bin/env python3
# coding=utf-8

FLPN = "Following Live"


def following_live() -> dict:
    """Following Live page dict."""
    return {
        "type": "streams",
        "category": FLPN,
        "page_name": FLPN
    }


def stream(category_name: str, category_id: str) -> dict:
    """Stream page dict."""
    return {
        "type": "streams",
        "category": category_name,
        "page_name": category_name,
        "category_id": category_id
    }


def video(video_type: str, user_id: str, user_name: str) -> dict:
    """Video page dict."""
    return {
        "type": "videos",
        "category": video_type,
        "page_name": f"{user_name} ({video_type})",
        "user_name": user_name,
        "user_id": user_id
    }
