#!/usr/bin/env python3
"""
Reddit API 连接测试脚本
======================

这个脚本专门用于测试Reddit API连接和认证。
它会逐步验证每个配置项，并提供详细的诊断信息。

使用方法：
python test_reddit_api.py
"""

import sys
import time
import traceback
from datetime import datetime

def test_imports():
    """测试必要的库导入"""
    print("🔍 测试Python库导入...")
    
    try:
        import praw
        print(f"✅ PRAW库版本: {praw.__version__}")
    except ImportError as e:
        print(f"❌ PRAW库导入失败: {e}")
        print("💡 请运行: pip install praw")
        return False
    
    try:
        import prawcore
        print(f"✅ PRAWCORE库已导入")
    except ImportError as e:
        print(f"❌ PRAWCORE库导入失败: {e}")
        return False
    
    try:
        from config import REDDIT_CONFIG
        print("✅ 配置文件导入成功")
        return True
    except ImportError as e:
        print(f"❌ 配置文件导入失败: {e}")
        return False

def test_configuration():
    """测试配置信息"""
    print("\n🔍 测试配置信息...")
    
    try:
        from config import REDDIT_CONFIG
        
        # 检查必要的配置项
        required_keys = ['client_id', 'client_secret', 'user_agent', 'username', 'password']
        
        for key in required_keys:
            if key in REDDIT_CONFIG and REDDIT_CONFIG[key]:
                # 隐藏敏感信息
                if key in ['client_secret', 'password']:
                    display_value = REDDIT_CONFIG[key][:4] + "***"
                else:
                    display_value = REDDIT_CONFIG[key]
                print(f"✅ {key}: {display_value}")
            else:
                print(f"❌ {key}: 未配置或为空")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        return False

def test_reddit_connection():
    """测试Reddit API连接"""
    print("\n🔍 测试Reddit API连接...")
    
    try:
        from config import REDDIT_CONFIG
        import praw
        import prawcore
        
        # 首先尝试script模式（完整认证）
        print("📡 尝试script模式认证...")
        try:
            reddit = praw.Reddit(
                client_id=REDDIT_CONFIG['client_id'],
                client_secret=REDDIT_CONFIG['client_secret'],
                user_agent=REDDIT_CONFIG['user_agent'],
                username=REDDIT_CONFIG['username'],
                password=REDDIT_CONFIG['password'],
                timeout=30
            )
            
            print("✅ Reddit客户端创建成功")
            
            # 测试认证
            print("🔐 测试script模式认证...")
            user = reddit.user.me()
            if user:
                print(f"✅ Script模式认证成功！登录用户: {user.name}")
                print(f"📊 用户统计: 链接业力={user.link_karma}, 评论业力={user.comment_karma}")
                return test_api_calls(reddit, "script模式")
            
        except prawcore.exceptions.OAuthException as e:
            if "Only script apps may use password auth" in str(e):
                print("⚠️ 应用类型不是script，尝试只读模式...")
            else:
                print(f"⚠️ Script模式认证失败: {e}")
        except Exception as e:
            print(f"⚠️ Script模式失败: {e}")
        
        # 尝试只读模式
        print("\n📡 尝试只读模式...")
        try:
            reddit_readonly = praw.Reddit(
                client_id=REDDIT_CONFIG['client_id'],
                client_secret=REDDIT_CONFIG['client_secret'],
                user_agent=REDDIT_CONFIG['user_agent'],
                timeout=30
            )
            
            print("✅ 只读模式Reddit客户端创建成功")
            return test_api_calls(reddit_readonly, "只读模式")
            
        except Exception as e:
            print(f"❌ 只读模式也失败: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Reddit连接测试失败: {e}")
        print(f"📋 错误详情:\n{traceback.format_exc()}")
        return False

def test_api_calls(reddit, mode_name):
    """测试API调用功能"""
    print(f"📝 测试{mode_name}API调用...")
    
    try:
        # 获取一个简单的subreddit信息
        subreddit = reddit.subreddit('python')
        print(f"✅ 成功访问subreddit: r/{subreddit.display_name}")
        print(f"📈 订阅者数量: {subreddit.subscribers:,}")
        
        # 测试搜索功能
        print("🔍 测试搜索功能...")
        search_results = list(subreddit.search('python', limit=1))
        if search_results:
            post = search_results[0]
            print(f"✅ 搜索测试成功，找到帖子: {post.title[:50]}...")
        else:
            print("⚠️ 搜索测试返回空结果")
        
        # 测试获取热门帖子
        print("🔥 测试获取热门帖子...")
        hot_posts = list(subreddit.hot(limit=1))
        if hot_posts:
            post = hot_posts[0]
            print(f"✅ 热门帖子测试成功: {post.title[:50]}...")
        else:
            print("⚠️ 热门帖子测试返回空结果")
        
        print(f"✅ 所有{mode_name}API测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ {mode_name}API调用测试失败: {e}")
        return False

def test_scraper_integration():
    """测试与scraper模块的集成"""
    print("\n🔍 测试Scraper模块集成...")
    
    try:
        from reddit_scraper import RedditScraper, create_search_parameters
        
        print("📦 创建Reddit Scraper实例...")
        scraper = RedditScraper()
        print("✅ Scraper创建成功")
        
        # 测试简单搜索
        print("🔍 测试简单搜索功能...")
        search_params = create_search_parameters(
            keywords=['test'],
            subreddits=['python'],
            limit=1
        )
        
        result = scraper.search_posts(search_params)
        
        print(f"✅ 搜索完成:")
        print(f"   找到帖子: {result.total_found}")
        print(f"   处理帖子: {result.total_processed}")
        print(f"   推广帖子: {result.promotional_count}")
        print(f"   执行时间: {result.execution_time:.2f}秒")
        print(f"   错误数量: {len(result.errors)}")
        
        if result.errors:
            print("⚠️ 搜索过程中的错误:")
            for error in result.errors:
                print(f"   - {error}")
        
        # 获取统计信息
        stats = scraper.get_session_statistics()
        print(f"📊 会话统计:")
        print(f"   处理帖子: {stats['session_stats']['posts_processed']}")
        print(f"   API请求: {stats['api_stats']['requests_made']}")
        
        scraper.cleanup()
        print("✅ Scraper集成测试完成")
        return True
        
    except Exception as e:
        print(f"❌ Scraper集成测试失败: {e}")
        print(f"📋 错误详情:\n{traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    print("🚀 Reddit API 连接测试开始")
    print("=" * 50)
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 测试步骤
    tests = [
        ("Python库导入", test_imports),
        ("配置信息", test_configuration),
        ("Reddit API连接", test_reddit_connection),
        ("Scraper模块集成", test_scraper_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name} - 通过")
            else:
                print(f"❌ {test_name} - 失败")
                
        except Exception as e:
            print(f"❌ {test_name} - 异常: {e}")
            results.append((test_name, False))
    
    # 总结报告
    print("\n" + "="*50)
    print("📋 测试结果总结")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name:20} : {status}")
    
    print(f"\n📊 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！Reddit API配置正确，系统可以正常使用。")
        return True
    else:
        print("⚠️ 部分测试失败，请检查上述错误信息并修复问题。")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 测试过程中发生未预期错误: {e}")
        print(f"📋 错误详情:\n{traceback.format_exc()}")
        sys.exit(1) 