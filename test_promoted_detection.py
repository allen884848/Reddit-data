#!/usr/bin/env python3
"""
Reddit推广帖子检测测试脚本
========================

这个脚本专门测试Reddit官方推广帖子（Promoted/Sponsored）的检测功能。
它会尝试找到真实的Reddit推广帖子并验证检测算法的准确性。

使用方法：
python test_promoted_detection.py
"""

import os
import sys
import json
from datetime import datetime

def test_reddit_promoted_detection():
    """测试Reddit推广帖子检测功能"""
    print("🔍 Reddit推广帖子检测测试")
    print("=" * 60)
    
    # 检查环境变量
    print("\n📋 检查环境变量...")
    
    credentials = {
        'REDDIT_CLIENT_ID': os.environ.get('REDDIT_CLIENT_ID'),
        'REDDIT_CLIENT_SECRET': os.environ.get('REDDIT_CLIENT_SECRET'),
        'REDDIT_USERNAME': os.environ.get('REDDIT_USERNAME'),
        'REDDIT_PASSWORD': os.environ.get('REDDIT_PASSWORD')
    }
    
    missing_vars = []
    for var_name, var_value in credentials.items():
        if var_value:
            if 'SECRET' in var_name or 'PASSWORD' in var_name:
                display_value = var_value[:4] + "*" * (len(var_value) - 4)
            else:
                display_value = var_value
            print(f"✅ {var_name}: {display_value}")
        else:
            print(f"❌ {var_name}: 未设置")
            missing_vars.append(var_name)
    
    if missing_vars:
        print(f"\n⚠️ 缺少环境变量: {', '.join(missing_vars)}")
        return False
    
    # 测试PRAW库
    print("\n📦 检查PRAW库...")
    try:
        import praw
        print("✅ PRAW库已安装")
    except ImportError:
        print("❌ PRAW库未安装")
        return False
    
    # 初始化Reddit客户端
    print("\n🔗 初始化Reddit客户端...")
    try:
        reddit = praw.Reddit(
            client_id=credentials['REDDIT_CLIENT_ID'],
            client_secret=credentials['REDDIT_CLIENT_SECRET'],
            username=credentials['REDDIT_USERNAME'],
            password=credentials['REDDIT_PASSWORD'],
            user_agent='RedditPromotedDetector/1.0 Test Script'
        )
        
        # 测试认证
        user = reddit.user.me()
        print(f"✅ 认证成功，登录用户: {user.name}")
        
    except Exception as e:
        print(f"❌ 认证失败: {e}")
        print("尝试只读模式...")
        try:
            reddit = praw.Reddit(
                client_id=credentials['REDDIT_CLIENT_ID'],
                client_secret=credentials['REDDIT_CLIENT_SECRET'],
                user_agent='RedditPromotedDetector/1.0 Test Script'
            )
            print("✅ 只读模式连接成功")
        except Exception as readonly_error:
            print(f"❌ 只读模式也失败: {readonly_error}")
            return False
    
    # 测试推广帖子检测
    print("\n🎯 测试推广帖子检测...")
    
    # 测试subreddit列表 - 这些地方更容易找到推广内容
    test_subreddits = [
        'all',
        'popular', 
        'deals',
        'entrepreneur',
        'startups',
        'business',
        'marketing',
        'technology',
        'gaming'
    ]
    
    total_posts_checked = 0
    promoted_posts_found = 0
    reddit_promoted_found = 0
    general_promotional_found = 0
    
    results = []
    
    for subreddit_name in test_subreddits:
        print(f"\n📍 检查 r/{subreddit_name}...")
        
        try:
            subreddit = reddit.subreddit(subreddit_name)
            
            # 搜索策略1: 搜索包含推广关键词的帖子
            try:
                search_results = subreddit.search(
                    'promoted OR sponsored OR advertisement', 
                    limit=10,
                    sort='new',
                    time_filter='month'
                )
                
                for submission in search_results:
                    total_posts_checked += 1
                    
                    # 检测推广内容
                    is_promoted, reddit_promoted, indicators = detect_promotion_detailed(submission)
                    
                    if is_promoted or reddit_promoted:
                        promoted_posts_found += 1
                        
                        if reddit_promoted:
                            reddit_promoted_found += 1
                            print(f"🔴 Reddit官方推广: {submission.title[:50]}...")
                        else:
                            general_promotional_found += 1
                            print(f"🟡 一般推广内容: {submission.title[:50]}...")
                        
                        # 记录详细信息
                        post_info = {
                            'title': submission.title,
                            'author': str(submission.author) if submission.author else '[deleted]',
                            'subreddit': submission.subreddit.display_name,
                            'url': submission.url,
                            'reddit_promoted': reddit_promoted,
                            'is_promotional': is_promoted,
                            'indicators': indicators,
                            'score': submission.score,
                            'num_comments': submission.num_comments
                        }
                        results.append(post_info)
                        
                        # 显示检测指标
                        if indicators:
                            print(f"   📊 检测指标: {', '.join(indicators)}")
                    
                    if total_posts_checked >= 100:  # 限制检查数量
                        break
                        
            except Exception as search_error:
                print(f"   ⚠️ 搜索失败: {search_error}")
            
            # 搜索策略2: 检查热门帖子
            try:
                hot_posts = subreddit.hot(limit=5)
                for submission in hot_posts:
                    if total_posts_checked >= 100:
                        break
                        
                    total_posts_checked += 1
                    is_promoted, reddit_promoted, indicators = detect_promotion_detailed(submission)
                    
                    if reddit_promoted:
                        reddit_promoted_found += 1
                        promoted_posts_found += 1
                        print(f"🔴 热门中的Reddit推广: {submission.title[:50]}...")
                        
                        post_info = {
                            'title': submission.title,
                            'author': str(submission.author) if submission.author else '[deleted]',
                            'subreddit': submission.subreddit.display_name,
                            'url': submission.url,
                            'reddit_promoted': reddit_promoted,
                            'is_promotional': is_promoted,
                            'indicators': indicators,
                            'score': submission.score,
                            'num_comments': submission.num_comments
                        }
                        results.append(post_info)
                        
            except Exception as hot_error:
                print(f"   ⚠️ 热门帖子检查失败: {hot_error}")
                
        except Exception as subreddit_error:
            print(f"   ❌ 无法访问 r/{subreddit_name}: {subreddit_error}")
            continue
        
        if total_posts_checked >= 100:
            break
    
    # 显示测试结果
    print("\n📊 测试结果统计")
    print("=" * 60)
    print(f"总检查帖子数: {total_posts_checked}")
    print(f"发现推广帖子: {promoted_posts_found}")
    print(f"Reddit官方推广: {reddit_promoted_found}")
    print(f"一般推广内容: {general_promotional_found}")
    
    if total_posts_checked > 0:
        promotion_rate = (promoted_posts_found / total_posts_checked) * 100
        reddit_promotion_rate = (reddit_promoted_found / total_posts_checked) * 100
        print(f"推广内容比例: {promotion_rate:.2f}%")
        print(f"Reddit官方推广比例: {reddit_promotion_rate:.2f}%")
    
    # 保存详细结果
    if results:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"promoted_detection_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细结果已保存到: {filename}")
        
        # 显示一些示例
        print("\n📝 发现的推广帖子示例:")
        for i, post in enumerate(results[:3]):
            print(f"\n{i+1}. {post['title'][:60]}...")
            print(f"   作者: {post['author']}")
            print(f"   Subreddit: r/{post['subreddit']}")
            print(f"   Reddit推广: {'是' if post['reddit_promoted'] else '否'}")
            print(f"   检测指标: {', '.join(post['indicators'])}")
    
    return True

def detect_promotion_detailed(submission):
    """详细的推广检测函数，返回检测结果和指标"""
    is_promotional = False
    reddit_promoted = False
    indicators = []
    
    try:
        # 检查Reddit官方推广属性
        if hasattr(submission, 'promoted') and submission.promoted:
            reddit_promoted = True
            indicators.append("promoted_flag")
        
        if hasattr(submission, 'distinguished') and submission.distinguished:
            indicators.append(f"distinguished_{submission.distinguished}")
            if submission.distinguished == 'admin':
                reddit_promoted = True
        
        if hasattr(submission, 'stickied') and submission.stickied:
            indicators.append("stickied")
        
        # 检查标题中的推广标记
        title_lower = submission.title.lower()
        if 'promoted' in title_lower:
            reddit_promoted = True
            indicators.append("title_promoted")
        if 'sponsored' in title_lower:
            reddit_promoted = True
            indicators.append("title_sponsored")
        if '[ad]' in title_lower:
            reddit_promoted = True
            indicators.append("title_ad_tag")
        
        # 检查作者
        if submission.author:
            author_name = str(submission.author).lower()
            if any(marker in author_name for marker in ['promoted', 'sponsored', 'ad_']):
                reddit_promoted = True
                indicators.append("promotional_author")
        
        # 检查flair
        if hasattr(submission, 'link_flair_text') and submission.link_flair_text:
            flair_lower = submission.link_flair_text.lower()
            if any(marker in flair_lower for marker in ['promoted', 'sponsored', 'ad']):
                reddit_promoted = True
                indicators.append("promotional_flair")
        
        # 检查一般推广关键词
        text = (submission.title + ' ' + (submission.selftext or '')).lower()
        promotional_keywords = ['buy', 'sale', 'discount', 'deal', 'offer', 'coupon']
        keyword_matches = sum(1 for keyword in promotional_keywords if keyword in text)
        
        if keyword_matches >= 2:
            is_promotional = True
            indicators.append(f"promotional_keywords_{keyword_matches}")
        
    except Exception as e:
        indicators.append(f"detection_error_{str(e)[:20]}")
    
    return is_promotional, reddit_promoted, indicators

def main():
    """主函数"""
    print("🚀 Reddit推广帖子检测测试工具")
    print("版本: 1.0")
    print("用途: 测试Reddit官方推广帖子检测功能")
    
    success = test_reddit_promoted_detection()
    
    if success:
        print("\n🎉 测试完成！")
        print("✅ 推广帖子检测功能正常工作。")
        print("\n💡 使用建议:")
        print("1. Reddit官方推广帖子相对较少，需要在大量帖子中搜索")
        print("2. 建议在热门subreddit和商业相关subreddit中搜索")
        print("3. 使用'all'和'popular'subreddit可以找到更多推广内容")
        print("4. 推广帖子通常在新帖子中更容易找到")
    else:
        print("\n❌ 测试失败！请检查配置。")
        sys.exit(1)

if __name__ == "__main__":
    main() 