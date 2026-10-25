from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import PerfilUsuario


def obtener_perfil_seguro(user):
    """Obtiene o crea de forma segura el perfil del usuario."""
    if not user.is_authenticated:
        return None
    try:
        return user.perfil
    except (PerfilUsuario.DoesNotExist, AttributeError):
        rol_default = PerfilUsuario.ROL_ADMIN if user.is_superuser else PerfilUsuario.ROL_ASESOR
        perfil, _ = PerfilUsuario.objects.get_or_create(usuario=user, defaults={'rol': rol_default})
        return perfil


def rol_requerido(roles_permitidos):
    """
    Decorador para restringir el acceso a vistas según los roles del usuario:
    - ADMINISTRADOR: Tiene acceso total siempre.
    - ASESOR: Tiene acceso a facturación y clientes.
    - BODEGUERO: Tiene acceso a inventario y productos.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            perfil = obtener_perfil_seguro(request.user)

            # El administrador o superusuario siempre tiene acceso total
            if request.user.is_superuser or (perfil and perfil.rol == PerfilUsuario.ROL_ADMIN):
                return view_func(request, *args, **kwargs)

            # Verificar si el rol del usuario está dentro de los permitidos
            if perfil and perfil.rol in roles_permitidos:
                return view_func(request, *args, **kwargs)

            # Si no tiene permiso, alertar y redirigir al Dashboard
            nombre_rol = perfil.get_rol_display() if perfil else 'Sin Rol'
            messages.error(
                request,
                f"Acceso Denegado: Tu rol actual ('{nombre_rol}') no tiene permisos para acceder a este módulo."
            )
            return redirect('dashboard')

        return _wrapped_view
    return decorator


# Accesos directos convenientes
def admin_requerido(view_func):
    return rol_requerido([PerfilUsuario.ROL_ADMIN])(view_func)


def asesor_o_admin(view_func):
    return rol_requerido([PerfilUsuario.ROL_ADMIN, PerfilUsuario.ROL_ASESOR])(view_func)


def bodeguero_o_admin(view_func):
    return rol_requerido([PerfilUsuario.ROL_ADMIN, PerfilUsuario.ROL_BODEGUERO])(view_func)
