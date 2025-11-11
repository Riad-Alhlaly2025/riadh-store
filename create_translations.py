# Script to create translation files
ar_content = '''# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.

msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2025-11-09 22:37+0300\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"Language: ar\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=6; plural=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5;\\n"

msgid "Home"
msgstr "الرئيسية"

msgid "Products"
msgstr "المنتجات"

msgid "Cart"
msgstr "السلة"

msgid "Orders"
msgstr "الطلبات"

msgid "Login"
msgstr "تسجيل الدخول"

msgid "Logout"
msgstr "تسجيل الخروج"

msgid "Register"
msgstr "تسجيل جديد"

msgid "Dashboard"
msgstr "لوحة التحكم"

msgid "Profile"
msgstr "الملف الشخصي"

msgid "Settings"
msgstr "الإعدادات"
'''

en_content = '''# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.

msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2025-11-09 22:37+0300\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"Language: en\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

msgid "Home"
msgstr "Home"

msgid "Products"
msgstr "Products"

msgid "Cart"
msgstr "Cart"

msgid "Orders"
msgstr "Orders"

msgid "Login"
msgstr "Login"

msgid "Logout"
msgstr "Logout"

msgid "Register"
msgstr "Register"

msgid "Dashboard"
msgstr "Dashboard"

msgid "Profile"
msgstr "Profile"

msgid "Settings"
msgstr "Settings"
'''

# Write Arabic translations
with open('c:/Users/PC/Desktop/myshop/locale/ar/LC_MESSAGES/django.po', 'w', encoding='utf-8') as f:
    f.write(ar_content)

# Write English translations
with open('c:/Users/PC/Desktop/myshop/locale/en/LC_MESSAGES/django.po', 'w', encoding='utf-8') as f:
    f.write(en_content)

print("Translation files created successfully!")