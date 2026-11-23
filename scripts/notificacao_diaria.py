"""
Notificação diária de NFs pendentes/vencidas.
Executado via Task Scheduler às 07:00 ou no logon.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import SessionLocal
from services.notificacao import obter_notificacoes, formatar_notificacao_texto


def enviar_notificacao_windows(titulo, mensagem):
    """Envia toast notification do Windows."""
    try:
        from plyer import notification
        notification.notify(
            title=titulo,
            message=mensagem,
            app_name='ControleNF',
            timeout=15,
        )
        print(f"[NOTIF] Toast enviado: {titulo}")
    except ImportError:
        # Fallback: usar PowerShell
        import subprocess
        ps_script = f'''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
        $textNodes = $template.GetElementsByTagName("text")
        $textNodes.Item(0).AppendChild($template.CreateTextNode("{titulo}")) | Out-Null
        $textNodes.Item(1).AppendChild($template.CreateTextNode("{mensagem}")) | Out-Null
        $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("ControleNF").Show($toast)
        '''
        try:
            subprocess.run(['powershell', '-Command', ps_script], capture_output=True)
            print(f"[NOTIF] Toast via PowerShell: {titulo}")
        except Exception as e:
            print(f"[NOTIF] Fallback - exibindo no console:")
            print(f"  {titulo}")
            print(f"  {mensagem}")


def main():
    """Verifica NFs pendentes e envia notificação."""
    print(f"\n[NOTIF] Verificando notificações...")

    db = SessionLocal()
    try:
        resumo = obter_notificacoes(db)
        texto = formatar_notificacao_texto(resumo)

        if resumo['total_alertas'] > 0:
            titulo = f"📋 ControleNF - {resumo['total_alertas']} alerta(s)"
            enviar_notificacao_windows(titulo, texto)
        else:
            print("[NOTIF] ✅ Nenhuma pendência encontrada.")

    except Exception as e:
        print(f"[NOTIF] ❌ Erro: {e}")
    finally:
        db.close()


if __name__ == '__main__':
    main()
