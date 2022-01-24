#!/usr/bin/env python3
# coding=utf-8


def check_auth_data():
    """Check user auth token before launch of the main program."""
    from twitchez import fs
    private_file = fs.private_data_path()
    # private_file is empty -> get auth token & write to private_file
    if not private_file.stat().st_size:
        from twitchez import auth
        auth.get_auth_token()
        print("Launch me again!")
        exit(69)
    # TODO: also check that the auth token hasn't expired and is still working


def main():
    check_auth_data()
    from twitchez import init
    init.main()


if __name__ == "__main__":
    main()
