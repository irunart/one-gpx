#!/usr/bin/env python3
"""
智能UTMB GPX处理器：
1. 从UTMB网站获取GPX轨迹
2. 检查是否已有CP点
3. 如果没有CP点，则添加从网站抓取的CP点信息
"""

import requests
import json
import re
import sys
import polyline
import gpxpy
import gpxpy.gpx
from math import radians, cos, sin, asin, sqrt

def calculate_distance(lat1, lon1, lat2, lon2):
    """计算两点间距离（米）"""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371000

def get_utmb_data(url):
    """获取UTMB页面数据"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content)
        if not match:
            return None
            
        json_data = json.loads(match.group(1))
        return json_data['props']['pageProps']['track']
    except Exception as e:
        print(f"Error fetching UTMB data: {e}")
        return None

def create_gpx_from_polyline(track_data, race_name="UTMB Race"):
    """从polyline创建GPX轨迹"""
    gpx = gpxpy.gpx.GPX()
    gpx.name = race_name
    gpx.description = f"Distance: {track_data.get('distance', 0)/1000:.1f}km"
    
    if 'polyline' in track_data:
        try:
            coordinates = polyline.decode(track_data['polyline'])
            
            gpx_track = gpxpy.gpx.GPXTrack()
            gpx_track.name = race_name
            gpx.tracks.append(gpx_track)
            
            gpx_segment = gpxpy.gpx.GPXTrackSegment()
            gpx_track.segments.append(gpx_segment)
            
            for lat, lon in coordinates:
                point = gpxpy.gpx.GPXTrackPoint(latitude=lat, longitude=lon)
                gpx_segment.points.append(point)
                
            print(f"✓ 创建轨迹: {len(coordinates)} 个轨迹点")
            return gpx
        except Exception as e:
            print(f"Error decoding polyline: {e}")
            return None
    return None

def has_checkpoints(gpx):
    """检查GPX是否已有CP点"""
    return len(gpx.waypoints) > 0

def find_closest_point_with_distance(track_points, target_lat, target_lon, cp_index=None, total_cps=None):
    """找到轨迹上最接近目标坐标的点并返回累计距离"""
    min_dist = float('inf')
    best_index = 0
    
    # 对于环形路线的特殊处理
    search_start = 0
    search_end = len(track_points)
    
    # 如果是最后一个CP点（终点），从轨迹后半段开始搜索
    if cp_index is not None and total_cps is not None and cp_index == total_cps - 1:
        search_start = len(track_points) // 2  # 从轨迹中点开始搜索
    
    for i in range(search_start, search_end):
        point = track_points[i]
        dist = calculate_distance(point.latitude, point.longitude, target_lat, target_lon)
        if dist < min_dist:
            min_dist = dist
            best_index = i
    
    # 计算累计距离
    cumulative_distance = 0
    for i in range(1, best_index + 1):
        prev_point = track_points[i-1]
        curr_point = track_points[i]
        segment_distance = calculate_distance(
            prev_point.latitude, prev_point.longitude,
            curr_point.latitude, curr_point.longitude
        )
        cumulative_distance += segment_distance
    
    return cumulative_distance / 1000, min_dist

def add_checkpoints_to_gpx(gpx, checkpoints):
    """将CP点添加到GPX文件"""
    if not gpx.tracks or not gpx.tracks[0].segments:
        print("⚠️  GPX文件中没有轨迹数据，无法计算CP距离")
        return False
    
    track_points = gpx.tracks[0].segments[0].points
    
    for i, cp in enumerate(checkpoints):
        name = f"{cp.get('uid', '')}: {cp.get('name', '')}" if cp.get('uid') else cp.get('name', '')
        
        # 计算CP点在轨迹上的实际距离
        distance_km, error_m = find_closest_point_with_distance(
            track_points, cp.get('lat'), cp.get('lon'), i, len(checkpoints)
        )
        
        waypoint = gpxpy.gpx.GPXWaypoint(
            latitude=cp.get('lat'),
            longitude=cp.get('lon'),
            name=name,
            description=f"CP - {distance_km:.1f}km (误差: {error_m:.0f}m)"
        )
        gpx.waypoints.append(waypoint)
        print(f"  + {name} @ {distance_km:.1f}km (误差: {error_m:.0f}m)")
    
    return True

def process_utmb_gpx(url, output_file, race_name=None):
    """智能处理UTMB GPX"""
    print(f"🔍 获取UTMB数据: {url}")
    
    # 1. 获取UTMB数据
    track_data = get_utmb_data(url)
    if not track_data:
        print("❌ 无法获取UTMB数据")
        return False
    
    race_distance = track_data.get('distance', 0) / 1000
    checkpoints = track_data.get('points', [])
    
    print(f"📊 赛事信息: {race_distance:.1f}km, {len(checkpoints)} 个CP点")
    
    # 2. 创建GPX轨迹
    gpx = create_gpx_from_polyline(track_data, race_name or "UTMB Race")
    if not gpx:
        print("❌ 无法创建GPX轨迹")
        return False
    
    # 3. 检查是否需要添加CP点
    if has_checkpoints(gpx):
        print("✓ GPX已包含CP点")
    else:
        print("🔧 添加CP点到GPX...")
        if add_checkpoints_to_gpx(gpx, checkpoints):
            print(f"✓ 成功添加 {len(checkpoints)} 个CP点")
        else:
            print("⚠️  CP点添加失败")
    
    # 4. 保存文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(gpx.to_xml())
    
    print(f"💾 GPX文件已保存: {output_file}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python smart_utmb_gpx.py <utmb_url> <output.gpx> [race_name]")
        print("Example: python smart_utmb_gpx.py https://translantau.utmb.world/races/tl120 TL120.gpx 'Trans Lantau 120'")
        sys.exit(1)
    
    url = sys.argv[1]
    output_file = sys.argv[2]
    race_name = sys.argv[3] if len(sys.argv) > 3 else None
    
    if process_utmb_gpx(url, output_file, race_name):
        print("🎉 处理完成!")
    else:
        print("❌ 处理失败!")
        sys.exit(1)
