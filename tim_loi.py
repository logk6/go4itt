import lyricsgenius

# Đăng ký và lấy API key từ Genius
genius = lyricsgenius.Genius("24_mjy08W4DXlM8nLeWCOYLo-nhM0fTE92c7dEOJ0WOCjaFAE-fPMjoOD1g2a2pD")

# Tìm bài hát theo lời gần đúng
song = genius.search_song("thu cuối")
if song:
    print("Tên bài hát:", song.title)
    print("Ca sĩ:", song.artist)
    print("Một đoạn lời:", song.lyrics[:200])  # chỉ in 200 ký tự đầu

#aqK5-vhl0QS-WnDMeEn0NP1axn2k4hg761r31i9A-kWbEQxPimPGazbQm-LWuXNQ   client id
#S0bxpg8LrSknJGZWnY1-NIdzImSmtjIcXD02xG7sQKucE4SaYh32vOFOuqfoAsQAM4r2Ezqb7prbAtFIVTTxKw client secret
#24_mjy08W4DXlM8nLeWCOYLo-nhM0fTE92c7dEOJ0WOCjaFAE-fPMjoOD1g2a2pD token