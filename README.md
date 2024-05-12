# gunadarma-vclass-discord-notify

Aplikasi Discord bot untuk mengirim notifkasi ke discord channel chat apabila ada tugas, materi, quiz, forum, dll di Gunadarma v-class (https://v-class.gunadarma.ac.id)

![image](https://github.com/mansuf/gunadarma-vclass-discord-notify/assets/43638783/a86ab4f7-fa38-4036-9e4e-44dd7ce71073)
![image](https://github.com/mansuf/gunadarma-vclass-discord-notify/assets/43638783/eceb06c6-c780-4367-be57-0d300db15ca9)
![image](https://github.com/mansuf/gunadarma-vclass-discord-notify/assets/43638783/6c4601a3-24bf-4b12-925e-d2aeadeef085)


## List aplikasi yang dibutuhkan untuk menjalakan aplikasi ini

- Python 3.10 dengan pip
- Git

## Cara menggunakannya

Duplikat repository ini menggunakan [git](https://git-scm.com)

```
git clone https://github.com/mansuf/gunadarma-vclass-discord-notify.git
cd gunadarma-vclass-discord-notify
```

Isi token discord bot anda di file `bot-token.secret.txt` (ganti "insert your discord bot token here" dengan token discord bot anda)

![image](https://github.com/mansuf/gunadarma-vclass-discord-notify/assets/43638783/b8cb7a38-94c1-44d5-aebe-35fbfa7fb53a)

Isi nama, host, port, user, dan password database di file `credential-db.secret.json`

**CATATAN:** Disini saya menggunakan MySQL database, anda bisa menggantinya jika menggunakan database yang berbeda, pergi ke website https://docs.djangoproject.com/en/5.0/ref/databases/ untuk melihat list database yang disupport oleh django

![image](https://github.com/mansuf/gunadarma-vclass-discord-notify/assets/43638783/80fb4740-7e33-4d17-9574-e1d8a8b99806)

Isi username dan password login anda untuk ke v-class.gunadarma.ac.id di file `credential-user.secret.json`

![image](https://github.com/mansuf/gunadarma-vclass-discord-notify/assets/43638783/7cb5f27c-4cad-46e7-b288-9f6462b7d619)

Isi channel id dan server discord id anda di file `discord-guild.secret.json`

![image](https://github.com/mansuf/gunadarma-vclass-discord-notify/assets/43638783/3a4ac138-ef74-4505-a90d-78a897fb2f8b)

Install libraries yang diperlukan untuk menjalankan aplikasi ini dengan menggunakan pip 

```sh
pip install -r requirements.txt
```

Setelah itu jalankan `start.py` dengan aplikasi Python

```sh
python start.py
```

