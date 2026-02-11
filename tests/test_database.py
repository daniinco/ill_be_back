import pytest
from repositories.user_repository import UserRepository
from repositories.advertisement_repository import AdvertisementRepository

@pytest.mark.asyncio
async def test_create_user():
    user_repo = UserRepository()
    user_id = await user_repo.create_user("aa", True)
    assert user_id is not None
    
    user = await user_repo.get_user(user_id)
    assert user is not None
    assert user['name'] == "aa"
    assert user['is_verified'] is True
    
    await user_repo.delete_user(user_id)

@pytest.mark.asyncio
async def test_create_advert():
    user_repo = UserRepository()
    ad_repo = AdvertisementRepository()
    
    user_id = await user_repo.create_user("aa", False)
    
    ad_id = await ad_repo.create_advertisement(
        user_id=user_id,
        item_id=1,
        name="bb",
        description="cc",
        category=2,
        images_qty=3
    )
    
    assert ad_id is not None
    
    ad = await ad_repo.get_advertisement(ad_id)
    assert ad is not None
    assert ad['name'] == "bb"
    assert ad['description'] == "cc"
    assert ad['category'] == 2
    assert ad['images_qty'] == 3
    assert ad['user_id'] == user_id
    assert ad['is_verified'] is False
    
    await ad_repo.delete_advertisement(ad_id)
    await user_repo.delete_user(user_id)

@pytest.mark.asyncio
async def test_unexist_user():
    user_repo = UserRepository()
    user = await user_repo.get_user(666)
    assert user is None

@pytest.mark.asyncio
async def test_get_unexist_advert():
    ad_repo = AdvertisementRepository()
    ad = await ad_repo.get_advertisement(666)
    assert ad is None

@pytest.mark.asyncio
async def test_delete_user_also_delete_advert():
    user_repo = UserRepository()
    ad_repo = AdvertisementRepository()
    
    user_id = await user_repo.create_user("", True)
    ad_id = await ad_repo.create_advertisement(
        user_id=user_id,
        item_id=1,
        name="",
        description="",
        category=2,
        images_qty=3
    )
    
    await user_repo.delete_user(user_id)
    
    ad = await ad_repo.get_advertisement(ad_id)
    assert ad is None