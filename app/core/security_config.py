import warnings

# Подавление предупреждения о crypt
warnings.filterwarnings("ignore", category=DeprecationWarning, message="'crypt' is deprecated")