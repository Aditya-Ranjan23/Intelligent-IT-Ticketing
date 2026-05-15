from dataclasses import dataclass


@dataclass(frozen=True)
class PlaybookEntry:
    id: str
    keywords: tuple[str, ...]
    suggested_steps: tuple[str, ...]
    base_confidence: float


UNKNOWN_ESCALATION = "UNKNOWN_ESCALATION"

UNKNOWN_STEPS = (
    "Collect exact error text, timestamp, and device name.",
    "Attach logs or a screenshot of the full error window.",
    "Route to L2 if the issue blocks work and no playbook matched.",
)

PLAYBOOK: tuple[PlaybookEntry, ...] = (
    PlaybookEntry(
        id="NET_VPN_DISCONNECT",
        keywords=("vpn", "disconnect", "tunnel", "anyconnect", "globalprotect"),
        suggested_steps=(
            "Restart the VPN client and reconnect to the preferred gateway.",
            "Clear saved VPN profile and re-import the enterprise profile from the IT portal.",
            "If Wi-Fi is unstable, switch to wired or another network and retry.",
        ),
        base_confidence=0.88,
    ),
    PlaybookEntry(
        id="MAIL_OUTLOOK_SYNC",
        keywords=("outlook", "sync", "mailbox", "exchange", "email stuck"),
        suggested_steps=(
            "Run Outlook in Safe Mode once, then restart normally.",
            "Repair Office from Apps & Features, then recreate the mail profile if needed.",
            "Confirm MFA / modern auth prompts are completed on mobile and desktop.",
        ),
        base_confidence=0.86,
    ),
    PlaybookEntry(
        id="ACC_PASSWORD_RESET",
        keywords=("password", "reset", "locked", "login", "cannot sign in"),
        suggested_steps=(
            "Use the self-service password portal; ensure CAPS LOCK is off.",
            "If AD lockout, wait 15 minutes or ask helpdesk for an unlock.",
            "Re-enroll MFA if the error references security defaults.",
        ),
        base_confidence=0.9,
    ),
    PlaybookEntry(
        id="HW_PRINT_SPOOLER",
        keywords=("printer", "print", "spooler", "queue"),
        suggested_steps=(
            "Clear the print queue and restart the Print Spooler service.",
            "Reinstall the printer driver from the manufacturer or corporate package.",
            "Verify the printer IP / queue name against the intranet printer list.",
        ),
        base_confidence=0.84,
    ),
    PlaybookEntry(
        id="APP_TEAMS_CRASH",
        keywords=("teams", "crash", "freeze", "microsoft teams"),
        suggested_steps=(
            "Fully quit Teams (system tray), clear cache %appdata%\\Microsoft\\Teams, relaunch.",
            "Update Teams and Windows; reboot if pending updates exist.",
            "If web works but desktop fails, use Teams web while desktop is repaired.",
        ),
        base_confidence=0.85,
    ),
)
