set $ctp-version v0.6.1
exec_always if [ ! -e ~/.themes/Catppuccin-Frappe-Standard-Lavender-dark ]; then \
  mkdir -p ~/.themes \
  && curl -L https://github.com/catppuccin/gtk/releases/download/$ctp-version/Catppuccin-Frappe-Standard-Lavender-dark.zip -o ~/.themes/catppuccin.zip \
  && unzip ~/.themes/catppuccin.zip -d ~/.themes/ \
  && rm -rf ~/.themes/catppuccin.zip; fi

export GTK_THEME='Catppuccin-Frappe-Standard-Lavender-dark:dark'
