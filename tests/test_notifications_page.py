
import pytest
from playwright.sync_api import expect


@pytest.mark.positive
@pytest.mark.smoke
def test_notifications_page_is_displayed(notifications_page):
    expect(notifications_page.notifications_title).to_be_visible()
    expect(notifications_page.mark_all_read_btn).to_be_visible()
    expect(notifications_page.all_radio).to_be_visible()
    expect(notifications_page.unread_radio).to_be_visible()


@pytest.mark.positive
@pytest.mark.navigation
def test_switch_between_all_and_unread(notifications_page):
    notifications_page.show_unread()
    expect(notifications_page.unread_radio).to_be_checked()

    notifications_page.show_all()
    expect(notifications_page.all_radio).to_be_checked()

    
# בדיקה: יש הודעות שלא נקראו -> Mark read על אחת, והרשימה של Unread קטנה ב-1.
#        אין הודעות שלא נקראו -> מופיע "You're all caught up" ואין כפתור Mark read.
@pytest.mark.positive
@pytest.mark.notifications
def test_mark_one_notification_as_read(notifications_page):
    notifications_page.show_unread()
    # מחכים שהרשימה תיטען: או שורה ראשונה או הודעת "אין כלום"
    expect(notifications_page.notifications.first
           .or_(notifications_page.all_caught_up_text)).to_be_visible()
    unread_before = notifications_page.notifications.count()
    print("\nUnread notifications before:", unread_before)

    if unread_before == 0:
        # מצב 1: הכל נקרא - אין מה לסמן
        expect(notifications_page.all_caught_up_text).to_be_visible()
        expect(notifications_page.mark_read_btns).to_have_count(0)
        return

    # מצב 2: יש הודעות שלא נקראו - מסמנים אחת
    notifications_page.mark_first_as_read()
    expect(notifications_page.notifications).to_have_count(unread_before - 1)


    # בדיקה: יש הודעות שלא נקראו -> Mark all as read, ורשימת Unread מתרוקנת.
#        אין הודעות שלא נקראו -> מופיע "You're all caught up".
@pytest.mark.positive
@pytest.mark.notifications
def test_mark_all_as_read(notifications_page):
    notifications_page.show_unread()
    expect(notifications_page.notifications.first
           .or_(notifications_page.all_caught_up_text)).to_be_visible()   # מחכים לסוף הטעינה
    unread_before = notifications_page.notifications.count()
    print("\nUnread notifications before:", unread_before)

    if unread_before == 0:
        # מצב 1: אין מה לסמן - כבר הכל נקרא
        expect(notifications_page.all_caught_up_text).to_be_visible()
        return

    # מצב 2: יש הודעות שלא נקראו - מסמנים את כולן בלחיצה אחת
    notifications_page.click_mark_all_read()

    expect(notifications_page.notifications).to_have_count(0)
    expect(notifications_page.all_caught_up_text).to_be_visible()