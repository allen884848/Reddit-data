#!/usr/bin/env python3
"""
Reddit API凭据测试脚本
====================

这个脚本用于测试Reddit API凭据是否正确配置。
可以在本地运行，也可以在Vercel环境中使用。

使用方法：
python test_reddit_credentials.py
"""

import os
import sys

def test_reddit_credentials():
    """测试Reddit API凭据"""
    print("🔍 Reddit API凭据测试")
    print("=" * 50)
    
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
            # 隐藏敏感信息
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
        print("\n📝 请在Vercel项目设置中添加这些环境变量：")
        print("1. 访问 https://vercel.com/dashboard")
        print("2. 选择您的项目")
        print("3. 进入 Settings > Environment Variables")
        print("4. 添加缺少的变量")
        return False
    
    # 测试PRAW库
    print("\n📦 检查PRAW库...")
    try:
        import praw
        print("✅ PRAW库已安装")
    except ImportError:
        print("❌ PRAW库未安装")
        print("请运行: pip install praw")
        return False
    
    # 测试Reddit API连接
    print("\n🔗 测试Reddit API连接...")
    
    try:
        # 尝试Script模式认证
        print("📡 尝试Script模式认证...")
        reddit = praw.Reddit(
            client_id=credentials['REDDIT_CLIENT_ID'],
            client_secret=credentials['REDDIT_CLIENT_SECRET'],
            username=credentials['REDDIT_USERNAME'],
            password=credentials['REDDIT_PASSWORD'],
            user_agent='RedditDataCollector/2.0 Test Script'
        )
        
        # 测试认证
        user = reddit.user.me()
        if user:
            print(f"✅ Script模式认证成功！")
            print(f"👤 登录用户: {user.name}")
            print(f"📊 链接业力: {user.link_karma}")
            print(f"💬 评论业力: {user.comment_karma}")
            
            # 测试搜索功能
            print("\n🔍 测试搜索功能...")
            try:
                subreddit = reddit.subreddit('test')
                posts = list(subreddit.hot(limit=3))
                print(f"✅ 搜索测试成功，找到 {len(posts)} 个帖子")
                
                # 显示第一个帖子信息
                if posts:
                    post = posts[0]
                    print(f"📝 示例帖子: {post.title[:50]}...")
                    print(f"👤 作者: {post.author}")
                    print(f"⬆️ 评分: {post.score}")
                
            except Exception as search_error:
                print(f"⚠️ 搜索测试失败: {search_error}")
            
            return True
            
    except Exception as script_error:
        print(f"⚠️ Script模式失败: {script_error}")
        
        # 尝试只读模式
        print("\n📡 尝试只读模式...")
        try:
            reddit = praw.Reddit(
                client_id=credentials['REDDIT_CLIENT_ID'],
                client_secret=credentials['REDDIT_CLIENT_SECRET'],
                user_agent='RedditDataCollector/2.0 Test Script'
            )
            
            # 测试只读访问
            subreddit = reddit.subreddit('test')
            posts = list(subreddit.hot(limit=1))
            print("✅ 只读模式连接成功")
            print("ℹ️ 注意：只读模式功能有限，建议修复Script模式认证")
            return True
            
        except Exception as readonly_error:
            print(f"❌ 只读模式也失败: {readonly_error}")
            return False

def print_troubleshooting_guide():
    """打印故障排除指南"""
    print("\n🔧 故障排除指南")
    print("=" * 50)
    
    print("\n❓ 常见问题及解决方案：")
    
    print("\n1️⃣ 401 Unauthorized 错误")
    print("   - 检查Client ID和Secret是否正确")
    print("   - 确认Reddit用户名和密码无误")
    print("   - 验证Reddit应用类型是否为'script'")
    
    print("\n2️⃣ 403 Forbidden 错误")
    print("   - 检查User Agent字符串")
    print("   - 确认请求频率不超过限制")
    print("   - 验证Reddit账户状态正常")
    
    print("\n3️⃣ 两步验证问题")
    print("   - 如果启用了两步验证，需要生成应用专用密码")
    print("   - 在Reddit设置中生成应用密码")
    print("   - 使用应用密码替代普通密码")
    
    print("\n4️⃣ 应用配置问题")
    print("   - 访问 https://www.reddit.com/prefs/apps")
    print("   - 确认应用类型为'script'")
    print("   - 检查重定向URI设置")
    
    print("\n📞 获取帮助：")
    print("   - Reddit API文档: https://www.reddit.com/dev/api/")
    print("   - PRAW文档: https://praw.readthedocs.io/")

def main():
    """主函数"""
    print("🚀 Reddit API凭据测试工具")
    print("版本: 1.0")
    print("用途: 验证Reddit API配置是否正确")
    
    success = test_reddit_credentials()
    
    if success:
        print("\n🎉 测试完成！Reddit API配置正确。")
        print("✅ 您可以正常使用Reddit数据采集功能。")
    else:
        print("\n❌ 测试失败！请检查配置。")
        print_troubleshooting_guide()
        sys.exit(1)

if __name__ == "__main__":
    main() 