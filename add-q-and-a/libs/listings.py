from pathlib import Path
from csv import reader
from os.path import getmtime
from json import load
from dataclasses import dataclass

@dataclass
class ListingInfo:
    FilePath : str = None
    LastModified : float = None
    Listing : dict = None



class Listings:
    def __init__(self) -> None:
        self.__cleanTextInfo = ListingInfo(f"{Path(__file__).parent.resolve()}/listings/clean.text.json", 
                                             getmtime(f"{Path(__file__).parent.resolve()}/listings/clean.text.json"),
                                             self.__get_listing_dict(f"{Path(__file__).parent.resolve()}/listings/clean.text.json"))
        self.__replaceInfo = ListingInfo(f"{Path(__file__).parent.resolve()}/listings/find.replace.json", 
                                             getmtime(f"{Path(__file__).parent.resolve()}/listings/find.replace.json"),
                                             self.__get_listing_dict(f"{Path(__file__).parent.resolve()}/listings/find.replace.json"))


    @staticmethod
    def __get_listing_dict(file_path):
        d : dict = dict()
        with open(file_path, encoding='utf-8') as f:
            data = load(f)
            for k, v in data.items():
                d[k] = v
        return d

    @property
    def CleanTextListing(self):
        # only reload the json if it was updated
        if self.__cleanTextInfo.LastModified != getmtime(self.__cleanTextInfo.FilePath):
            self.__cleanTextInfo.Listing = Listings.__get_listing_dict(self.__cleanTextInfo.FilePath)
            self.__file_modified_at = getmtime(self.__cleanTextInfo.FilePath)
        return self.__cleanTextInfo.Listing

    @property
    def FindReplaceListing(self):
        # only reload the json if it was updated
        if self.__replaceInfo.LastModified != getmtime(self.__replaceInfo.FilePath):
            self.__replaceInfo.Listing = Listings.__get_listing_dict(self.__replaceInfo.FilePath)
            self.__file_modified_at = getmtime(self.__replaceInfo.FilePath)
        return self.__replaceInfo.Listing
