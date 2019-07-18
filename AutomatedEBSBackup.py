#Backup All in-use volumes in all regions

import boto3

def lambda handler(event,context):
	ec2 = boto3.client('ec2')
	
	#Get List of regions
	regions = ec2.describe_regions().get('Regions',[])
	
	#Iterate over Regions
	for region in regions:
		print("Checking region %s" % region['RegionName'])
		reg = region['RegionName]
		
		#Connect to Region
		ec2 = boto3.client('ec2',region_name = reg)
		
		#Get all in-use volumes in all regions
		result = ec2.describe_volume(Filter = [{'Name':'status', 'Values':['in-use']}])
		
		for volume in result['Volumes']:
			print ("Backing up %s in %s" % volume['VolumeId'], volume['AvailabilityZone'])
			
			#Create Snapshot
			result = ec2.create_snapshot(VolumeId=volume['VolumeId'],Description='Created by Lambda backup function for EBS Snapshots')
			
			#Get Snapshot Resource
			ec2resource = boto3.resource('ec2',region_name=reg)
			snapshot = ec2resource.Snapshot(result['SnapshotId'])
			
			volumename = 'By Lambda'
			
			#Find name tag for volume if it exists
			if 'Tage' in volume:
				for tags in volume['Tags']:
					if tags['Key']=='Name':
						volumename = tags['Value']
			
			#Add Volume name to snapshot for easier identification
			snapshot.create_tags(Tags=[{'Key':'Name','Value':volumename}])
			
		
